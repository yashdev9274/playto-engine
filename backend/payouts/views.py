import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from merchants.authentication import MerchantAuthentication
from idempotency.models import IdempotencyRecord
from payouts.models import Payout
from payouts.serializers import PayoutSerializer, PayoutCreateSerializer
from payouts.services import PayoutService, InsufficientFundsError
from payouts.tasks import process_payout


class PayoutViewSet(APIView):
    """GET /api/v1/payouts, POST /api/v1/payouts"""
    authentication_classes = [MerchantAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """GET - List all payouts for merchant"""
        payouts = Payout.objects.filter(merchant=request.merchant).order_by('-created_at')
        serializer = PayoutSerializer(payouts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """POST - Create new payout with idempotency"""
        idempotency_key = request.headers.get('Idempotency-Key')

        # Validate idempotency key present
        if not idempotency_key:
            return Response(
                {'error': 'Idempotency-Key header required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate UUID format
        try:
            idempotency_key = uuid.UUID(idempotency_key)
        except ValueError:
            return Response(
                {'error': 'Invalid UUID format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check idempotency - already processed?
        record = IdempotencyRecord.objects.filter(
            merchant=request.merchant,
            key=idempotency_key,
            expires_at__gt=timezone.now()
        ).first()

        if record:
            return Response(record.response, status=status.HTTP_200_OK)

        # Validate request body
        serializer = PayoutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create payout with concurrency lock
        try:
            payout = PayoutService.create_payout(
                merchant_id=request.merchant.id,
                amount_paise=serializer.validated_data['amount_paise'],
                bank_account_id=serializer.validated_data['bank_account_id'],
                idempotency_key=idempotency_key
            )
        except InsufficientFundsError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Store idempotency record
        payout_response = PayoutSerializer(payout).data
        IdempotencyRecord.objects.create(
            merchant=request.merchant,
            key=idempotency_key,
            response=payout_response,
            request_hash=str(idempotency_key),
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Queue Celery task (async processing)
        process_payout.delay(str(payout.id))

        return Response(payout_response, status=status.HTTP_201_CREATED)