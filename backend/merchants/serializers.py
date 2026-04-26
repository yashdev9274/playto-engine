from rest_framework import serializers
from .models import Merchant

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'email']
        read_only_fields = ['id', 'name', 'email']