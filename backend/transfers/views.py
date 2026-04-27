from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from merchants.authentication import MerchantAuthentication
from .models import Transfer
from .serializers import TransferSerializer, TransferCreateSerializer
from .services import (
    TransferService, 
    RecipientNotFoundError, 
    SelfTransferError, 
    InsufficientFundsError
)


class TransferViewSet(APIView):
    """GET /api/v1/transfers, POST /api/v1/transfers"""
    authentication_classes = [MerchantAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all transfers for current merchant (sent and received)"""
        transfers = Transfer.objects.filter(
            from_merchant=request.merchant
        ) | Transfer.objects.filter(
            to_merchant=request.merchant
        )
        transfers = transfers.order_by('-created_at')
        
        serializer = TransferSerializer(transfers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new transfer to another merchant"""
        serializer = TransferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            transfer = TransferService.create_transfer(
                from_merchant=request.merchant,
                to_merchant_email=serializer.validated_data['to_merchant_email'],
                amount_paise=serializer.validated_data['amount_paise']
            )
        except RecipientNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except SelfTransferError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except InsufficientFundsError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            TransferSerializer(transfer).data, 
            status=status.HTTP_201_CREATED
        )