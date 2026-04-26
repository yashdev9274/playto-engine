from django.db import transaction
from django.db.models import Sum, Case, When, F
from .models import LedgerEntry

class LedgerService:
    @staticmethod
    def calculate_balance(merchant_id):
        """Calculate balance using database aggregation - THE INVARIANT"""
        result = LedgerEntry.objects.filter(merchant_id=merchant_id).aggregate(
            balance=Sum(
                Case(

                    When(entry_type='credit', then=F('amount_paise')),
                    When(entry_type='debit',then=-F('amount_paise')),
                    default=0,
                )
            )
        )
        return result['balance'] or 0

    @staticmethod
    def calculate_held_balance(merchant_id):
        """Calculate held balance (debits for pending payouts)"""
        from payouts.models import Payout
        from django.db.models import Sum

        result = Payout.objects.filter(
            merchant_id=merchant_id,
            status__in=['pending', 'processing']
        ).aggregate(total=Sum('amount_paise'))

        return result ['total'] or 0

    @staticmethod
    @transaction.atomic
    def create_entry(merchant_id, entry_type, amount_paise, reference_id=None,
    reference_type=None, description=None):
        """Create ledger entry atomically"""
        return LedgerEntry.objects.create(
            merchant_id=merchant_id,
            entry_type=entry_type,
            amount_paise=amount_paise,
            reference_id=reference_id,
            reference_type=reference_type,
            description=description
        )
