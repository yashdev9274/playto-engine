from django.db import models
from core.models import UUIDModel
from merchants.models import Merchant

class IdempotencyRecord(UUIDModel):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='idempotency_records')
    key = models.UUIDField()
    response = models.JSONField()
    request_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'idempotency_records'
        constraints = [
            models.UniqueConstraint('merchant', 'key', name='unique_merchant_key'),
        ]
        indexes = [
            models.Index(fields=['expires_at']),
        ]