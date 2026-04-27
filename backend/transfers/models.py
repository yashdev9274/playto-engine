import uuid
from django.db import models
from core.models import UUIDModel
from merchants.models import Merchant


class Transfer(UUIDModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    from_merchant = models.ForeignKey(
        Merchant, 
        on_delete=models.CASCADE, 
        related_name='transfers_sent'
    )
    to_merchant = models.ForeignKey(
        Merchant, 
        on_delete=models.CASCADE, 
        related_name='transfers_received'
    )
    amount_paise = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transfers'
        indexes = [
            models.Index(fields=['from_merchant', 'created_at']),
            models.Index(fields=['to_merchant', 'created_at']),
        ]