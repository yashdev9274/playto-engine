import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playto.settings')
django.setup()

from merchants.models import Merchant
from ledger.models import LedgerEntry
from ledger.services import LedgerService
from payouts.models import Payout, IdempotencyRecord
from idempotency.models import IdempotencyRecord as IdempRecord
from django.utils import timezone
from datetime import timedelta
import uuid


def test_idempotency():
    """Test that duplicate requests return same response and don't create duplicates"""
    print("\n=== TEST: Idempotency ===")

    # Get or create test merchant
    merchant, _ = Merchant.objects.get_or_create(
        email='idempotency_test@test.com',
        defaults={
            'name': 'Idempotency Test',
            'api_key': 'test_idempotency_key_456'
        }
    )

    # Clear existing data
    LedgerEntry.objects.filter(merchant=merchant).delete()
    Payout.objects.filter(merchant=merchant).delete()
    IdempRecord.objects.filter(merchant=merchant).delete()

    # Add balance
    LedgerService.create_entry(
        merchant_id=merchant.id,
        entry_type='credit',
        amount_paise=50000,
        description='Test balance'
    )

    # Use the same idempotency key for two requests
    test_key = uuid.UUID('11111111-1111-1111-1111-111111111111')

    # First request - create payout
    from payouts.services import PayoutService
    payout1 = PayoutService.create_payout(
        merchant_id=merchant.id,
        amount_paise=10000,
        bank_account_id='TEST123',
        idempotency_key=test_key
    )
    print(f"First request created payout: {payout1.id}")

    # Second request with same key - should return same payout (no new one created)
    payout2 = PayoutService.create_payout(
        merchant_id=merchant.id,
        amount_paise=10000,
        bank_account_id='TEST123',
        idempotency_key=test_key
    )
    print(f"Second request returned payout: {payout2.id}")

    # Check only one payout was created
    payout_count = Payout.objects.filter(merchant=merchant).count()
    print(f"Total payouts in database: {payout_count}")

    # Check idempotency record exists
    record = IdempRecord.objects.filter(
        merchant=merchant,
        key=test_key
    ).first()
    print(f"Idempotency record exists: {record is not None}")

    # Verify
    assert payout1.id == payout2.id, "Same idempotency key should return same payout"
    assert payout_count == 1, f"Should have exactly 1 payout, got {payout_count}"
    assert record is not None, "Idempotency record should exist"

    # Test key expiration
    print("\n--- Testing key expiration ---")
    expired_key = uuid.UUID('22222222-2222-2222-2222-222222222222')

    # Create an expired idempotency record
    IdempRecord.objects.create(
        merchant=merchant,
        key=expired_key,
        response={'test': 'old'},
        request_hash='test',
        expires_at=timezone.now() - timedelta(hours=1)  # Already expired
    )

    # Now a new request with this key should succeed (create new payout)
    payout3 = PayoutService.create_payout(
        merchant_id=merchant.id,
        amount_paise=10000,
        bank_account_id='TEST456',
        idempotency_key=expired_key
    )
    print(f"Expired key created new payout: {payout3.id}")

    # Should have 2 payouts now
    payout_count_after = Payout.objects.filter(merchant=merchant).count()
    assert payout_count_after == 2, f"Expired key should allow new payout, got {payout_count_after}"

    print("✅ TEST PASSED: Idempotency test passed")
    return True


if __name__ == '__main__':
    try:
        test_idempotency()
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()