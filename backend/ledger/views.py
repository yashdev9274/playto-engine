from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Case, When, F

from merchants.authentication import MerchantAuthentication
from ledger.models import LedgerEntry
from ledger.serializers import LedgerEntrySerializer
from ledger.services import LedgerService


class BalanceView(APIView):
    """GET /api/v1/merchants/me/balance"""
    authentication_classes = [MerchantAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = request.merchant
        
        # Total balance = credits - debits
        total_balance = LedgerService.calculate_balance(merchant.id)
        
        # Held balance = pending + processing payouts
        from payouts.models import Payout
        from django.db.models import Sum as DBSum
        
        held_result = Payout.objects.filter(
            merchant=merchant,
            status__in=['pending', 'processing']
        ).aggregate(total=DBSum('amount_paise'))
        held_balance = held_result['total'] or 0
        
        # Available = total - held
        available_balance = total_balance - held_balance

        return Response({
            'available_balance_paise': available_balance,
            'held_balance_paise': held_balance,
            'total_balance_paise': total_balance
        })


class LedgerView(APIView):
    """GET /api/v1/merchants/me/ledger"""
    authentication_classes = [MerchantAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = request.merchant
        entry_type = request.query_params.get('entry_type')
        
        queryset = LedgerEntry.objects.filter(merchant=merchant)
        
        if entry_type:
            queryset = queryset.filter(entry_type=entry_type)
        
        queryset = queryset.order_by('-created_at')
        
        # Paginate
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        results = queryset[start:end]
        
        serializer = LedgerEntrySerializer(results, many=True)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })