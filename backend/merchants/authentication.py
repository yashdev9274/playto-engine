from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Merchant

class MerchantAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        try:
            auth_type, token = auth_header.split(' ')
            if auth_type.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        try:
            merchant = Merchant.objects.get(api_key=token)
        except Merchant.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        
        request.merchant = merchant
        return (merchant, token)

    def authenticate_header(self, request):
        return 'Bearer'