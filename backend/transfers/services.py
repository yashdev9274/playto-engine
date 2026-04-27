from django.db import transaction
from django.utils import timezone
from merchants.models import Merchant
from ledger.services import LedgerService
from .models import Transfer


class TransferService:
    @staticmethod
    @transaction.atomic
    def create_transfer(from_merchant, to_merchant_email, amount_paise):
        """Transfer funds between merchants atomically."""
        
        # Get destination merchant
        try:
            to_merchant = Merchant.objects.get(email=to_merchant_email)
        except Merchant.DoesNotExist:
            raise RecipientNotFoundError(f"Recipient {to_merchant_email} not found")
        
        # Cannot transfer to self
        if from_merchant.id == to_merchant.id:
            raise SelfTransferError("Cannot transfer to your own account")
        
        # Lock both merchants to prevent race conditions
        from_m = Merchant.objects.select_for_update(nowait=True).get(id=from_merchant.id)
        to_m = Merchant.objects.select_for_update(nowait=True).get(id=to_merchant.id)
        
        # Check sender balance
        balance = LedgerService.calculate_balance(from_merchant.id)
        if balance < amount_paise:
            raise InsufficientFundsError(
                f"Insufficient balance. Available: {balance}, Requested: {amount_paise}"
            )
        
        # Create debit entry (sender)
        LedgerService.create_entry(
            merchant_id=from_merchant.id,
            entry_type='debit',
            amount_paise=amount_paise,
            reference_type='transfer',
            description=f'Transfer to {to_merchant.email}'
        )
        
        # Create credit entry (receiver)
        LedgerService.create_entry(
            merchant_id=to_merchant.id,
            entry_type='credit',
            amount_paise=amount_paise,
            reference_type='transfer',
            description=f'Transfer from {from_merchant.email}'
        )
        
        # Create transfer record
        transfer = Transfer.objects.create(
            from_merchant=from_merchant,
            to_merchant=to_merchant,
            amount_paise=amount_paise,
            status='completed',
            completed_at=timezone.now()
        )
        
        return transfer


class RecipientNotFoundError(Exception):
    pass


class SelfTransferError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass