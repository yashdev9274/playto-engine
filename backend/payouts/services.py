from django.db import transaction
from django.db.models import F
from merchants.models import Merchant
from ledger.services import LedgerService
from .models import Payout


class InsufficientFundsError(Exception):
    pass

class PayoutService:
    @staticmethod
    @transaction.atomic
    def create_payout(merchant_id, amount_paise, bank_account_id, idempotency_key):
        """Create payout with SELECT FOR UPDATE lock - prevents concurrent overdrafts"""

        merchant = Merchant.objects.select_for_update(nowait=True).get(id=merchant_id)

        balance = LedgerService.calculate_balance(merchant_id)

        if balance < amount_paise:
            raise InsufficientFundsError(f"Insufficient balance. Available: {balance}, Requested: {amount_paise}")

        payout = Payout.objects.create(
            merchant_id=merchant_id,
            amount_paise=amount_paise,
            bank_account_id=bank_account_id,
            idempotency_key=idempotency_key,
            status='pending'
        )

        LedgerService.create_entry(
            merchant_id=merchant_id,
            entry_type='debit',
            amount_paise=amount_paise,
            reference_id=payout.id,
            reference_type='payout',
            description=f'Payout initiated: {payout.id}'
        )

        return payout

    @staticmethod
    @transaction.atomic
    def return_funds(payout):
        """Return funds atomically when payout fails"""
        LedgerService.create_entry(
            merchant_id=payout.merchant_id,
            entry_type='credit',
            amount_paise=payout.amount_paise,
            reference_id=payout.id,
            reference_type='payout',
            description=f'Payout failed, funds returned: {payout.failure_reason}'
        )
