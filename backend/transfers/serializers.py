from rest_framework import serializers
from .models import Transfer


class TransferSerializer(serializers.ModelSerializer):
    from_merchant_email = serializers.EmailField(source='from_merchant.email', read_only=True)
    to_merchant_email = serializers.EmailField(source='to_merchant.email', read_only=True)
    
    class Meta:
        model = Transfer
        fields = [
            'id', 
            'from_merchant', 'from_merchant_email',
            'to_merchant', 'to_merchant_email',
            'amount_paise', 
            'status', 
            'failure_reason',
            'created_at', 
            'completed_at'
        ]
        read_only_fields = fields


class TransferCreateSerializer(serializers.Serializer):
    to_merchant_email = serializers.EmailField()
    amount_paise = serializers.IntegerField(min_value=1)