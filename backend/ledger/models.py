from django.db import models
from core.models import UUIDModel
from merchants.models import Merchant

class LedgerEntry(UUIDModel):
    ENTRY_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    REFERENCE_TYPES = [
        ('payment', 'Payment'),
        ('payout', 'Payout'),
    ]
    
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='ledger_entries')
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount_paise = models.BigIntegerField()  # CRITICAL: No floats
    reference_id = models.UUIDField(null=True, blank=True)
    reference_type = models.CharField(max_length=20, choices=REFERENCE_TYPES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ledger_entries'
        indexes = [
            models.Index(fields=['merchant', 'created_at']),
            models.Index(fields=['merchant', 'entry_type']),
        ]