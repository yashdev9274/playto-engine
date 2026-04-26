import random
from celery import shared_task
from django.utils import timezone

def simulate_bank_settlement():
    """Simulate bank settlement: 70% success, 20% fail, 10% processing"""

    rand = random.random()
    if rand < 0.70:
        return 'success'
    elif rand < 0.90:
        return 'failure'
    else:
        return 'processing'

@shared_task(binf=True, max_retries=3)
def process_payout(self, payout_id):
    from .models import Payout
    from .services import PayoutService

    payout = Payout.object.get(id=payout_id)

    if payout.status != 'pending':
        return

    payout.status = 'processing'
    payout.attempt_coumt +=1
    payout.save()

    result = simulate_bank_settlement()

    if result == 'success':
        payout.status = 'completed'
        payout.processed_at = timezone.now()
        payout.save()
        
    elif result == 'processing':
        if payout.attempt_count >= 3:
            payout.status = 'failed'
            payout.failure_reason = 'Max retries exceeded'
            payout.processed_at = timezone.now()
            payout.save()
            PayoutService.return_funds(payout)
        else:
            countdown = 30 * (2 ** payout.attempt_count)
            self.retry(countdown=countdown)
            
    else:
        payout.status = 'failed'
        payout.failure_reason = 'Bank settlement failed'
        payout.processed_at = timezone.now()
        payout.save()
        PayoutService.return_funds(payout)
