from rest_framework import serializers
from .models import Payout

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields=['id', 'amount_paise', 'bank_account_id', 'status', 'attempt_count', 'failure_reason', 'created_at', 'processed_at']
        read_only_fields = ['id', 'status', 'attempt_count', 'failure_reason', 'created_at', 'processed_at']


class PayoutCreateSerializer(serializers.Serializer):
    amount_paise = serializers.IntegerField(min_value=1)
    bank_account_id = serializers.CharField(max_length=50)