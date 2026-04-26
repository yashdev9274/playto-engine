import os
import django
import secrets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playto.settings')
django.setup()

from merchants.models import Merchant
from ledger.models import LedgerEntry
from ledger.services import LedgerService

def seed():
    print("Seeding database...")
    
    # Create merchants
    merchants_data = [
        {
            'name': 'Acme Agency',
            'email': 'acme@example.com',
            'api_key': secrets.token_hex(32)
        },
        {
            'name': 'TechFreelancer',
            'email': 'tech@example.com',
            'api_key': secrets.token_hex(32)
        },
        {
            'name': 'Design Studio',
            'email': 'design@example.com',
            'api_key': secrets.token_hex(32)
        },
    ]
    
    merchants = []
    for data in merchants_data:
        merchant, created = Merchant.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        merchants.append(merchant)
        if created:
            print(f"Created merchant: {merchant.name}")
        else:
            print(f"Merchant exists: {merchant.name}")
    
    # Create credit entries for each merchant
    for i, merchant in enumerate(merchants):
        # Create 5 credit entries per merchant
        for j in range(5):
            amount = (i + 1) * 10000 + (j * 5000)  # Different amounts
            LedgerEntry.objects.create(
                merchant=merchant,
                entry_type='credit',
                amount_paise=amount,
                description=f'Payment from client {j + 1}',
                reference_type='payment'
            )
        print(f"Created credits for: {merchant.name}")
    
    print("\nMerchant API Keys:")
    for merchant in Merchant.objects.all():
        print(f"  {merchant.name}: {merchant.api_key}")
    
    print("\nSeeding complete!")

if __name__ == '__main__':
    seed()