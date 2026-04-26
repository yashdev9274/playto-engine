import os
import django
import threading
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playto.settings')
django.setup()

from merchants.models import Merchant
from ledger.models import LedgerEntry
from ledger.services import LedgerService
from payouts.services import PayoutService, InsufficientFundsError
from payouts.models import Payout
import uuid


def test_concurrent_payouts():
    """Test that only one of two simultaneous payout requests succeeds"""
    print("\n=== TEST: Concurrent Payouts ===")

    # Get or create test merchant
    merchant, _ = Merchant.objects.get_or_create(
        email='concurrency_test@test.com',
        defaults={
            'name': 'Concurrency Test',
            'api_key': 'test_concurrency_key_123'
        }
    )

    # Clear existing data
    LedgerEntry.objects.filter(merchant=merchant).delete()
    Payout.objects.filter(merchant=merchant).delete()

    # Add exactly 10000 paise (100 INR)
    LedgerService.create_entry(
        merchant_id=merchant.id,
        entry_type='credit',
        amount_paise=10000,
        description='Test balance'
    )

    balance = LedgerService.calculate_balance(merchant.id)
    print(f"Initial balance: {balance} paise (100 INR)")

    results = {'success': 0, 'failed': 0, 'errors': []}

    def try_payout():
        try:
            payout = PayoutService.create_payout(
                merchant_id=merchant.id,
                amount_paise=6000,  # 60 INR each
                bank_account_id='TEST123',
                idempotency_key=uuid.uuid4()
            )
            results['success'] += 1
            print(f"  Thread succeeded with payout: {payout.id}")
        except InsufficientFundsError as e:
            results['failed'] += 1
            print(f"  Thread failed with insufficient funds: {e}")
        except Exception as e:
            results['errors'].append(str(e))
            print(f"  Thread error: {e}")

    # Create two threads trying to withdraw 60 INR simultaneously
    threads = [threading.Thread(target=try_payout) for _ in range(2)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(f"Results: {results['success']} succeeded, {results['failed']} rejected")

    # Final balance should be 4000 (10000 - 6000)
    final_balance = LedgerService.calculate_balance(merchant.id)
    print(f"Final balance: {final_balance} paise")

    # Exactly one should succeed
    assert results['success'] == 1, f"Expected 1 success, got {results['success']}"
    assert results['failed'] == 1, f"Expected 1 rejected, got {results['failed']}"
    assert final_balance == 4000, f"Expected 4000 paise, got {final_balance}"

    print("✅ TEST PASSED: Concurrency test passed")
    return True


if __name__ == '__main__':
    try:
        test_concurrent_payouts()
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")