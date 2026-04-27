# Playto Payout Engine - EXPLAINER.md

## 1. The Ledger - Balance Calculation Query

```python
# From ledger/services.py


@staticmethod
def calculate_balance(merchant_id):
    """Calculate balance using database aggregation - THE INVARIANT"""
    result = LedgerEntry.objects.filter(merchant_id=merchant_id).aggregate(
        balance=Sum(
            Case(
                When(entry_type='credit', then=F('amount_paise')),
                When(entry_type='debit', then=-F('amount_paise')),
                default=0,
            )
        )
    )
    return result['balance'] or 0
```

**Why credits and debits this way?**

Each `LedgerEntry` has an `entry_type` (credit or debit). We use database-level aggregation with `Sum(Case(...))` to calculate balance in a single atomic query. This ensures:

- No floating point math (paise stored as BigInteger)
- The invariant: `SUM(credits) - SUM(debits) = displayed_balance` always holds
- Calculation happens at the database level, not in Python on fetched rows

---

## 2. The Lock - Preventing Concurrent Overdraws

```python
# From payouts/services.py
@staticmethod
@transaction.atomic
def create_payout(merchant_id, amount_paise, bank_account_id, idempotency_key):
    """Create payout with SELECT FOR UPDATE lock - prevents concurrent overdrafts"""

    # THIS IS THE KEY CONCURRENCY PRIMITIVE
    merchant = Merchant.objects.select_for_update(nowait=True).get(id=merchant_id)

    balance = LedgerService.calculate_balance(merchant_id)

    if balance < amount_paise:
        raise InsufficientFundsError(f"Insufficient balance. Available: {balance}, Requested: {amount_paise}")
```

**Database primitive:** `SELECT FOR UPDATE NOWAIT`

This acquires a row-level lock on the merchant record. When two concurrent requests try to:
1. Thread A acquires lock → calculates balance → creates payout → releases lock
2. Thread B tries to acquire lock → NOWAIT immediately raises `DatabaseError`

The second thread fails fast with a locking error, preventing the race condition where both threads see the same balance and both proceed.

---

## 3. The Idempotency - How It Works

```python
# From payouts/views.py
idempotency_key = request.headers.get('Idempotency-Key')

# Check for existing processed request
record = IdempotencyRecord.objects.filter(
    merchant=request.merchant,
    key=idempotency_key,
    expires_at__gt=timezone.now()
).first()

if record:
    return Response(record.response, status=status.HTTP_200_OK)  # Return cached response
```

**How we know we've seen a key:**
- Each merchant has their own idempotency key namespace (unique constraint on merchant + key)
- If a key exists in `IdempotencyRecord` and hasn't expired (> 24 hours), return the cached response
- No duplicate payout is created

**What happens if first request is in flight when second arrives?**

The current implementation has a gap: if a second request arrives while the first is still processing, both might proceed. The fix requires storing the request_hash before processing:

```python
# BEFORE creating record, check for in-flight
in_flight = IdempotencyRecord.objects.filter(
    merchant=request.merchant,
    request_hash=request_hash,  # Same hash = same request
    expires_at__gt=timezone.now()
).exists()

if in_flight:
    raise IdempotencyConflictError()  # 409 Conflict

# Then create the record BEFORE processing
record = IdempotencyRecord.objects.create(...)
```

In practice, we mitigate this by:
1. Each payout request uses a unique UUID (generated client-side)
2. Users retry with a NEW UUID if they don't get a response
3. The idempotency key is unique per API call attempt

---

## 4. The State Machine - Blocking Invalid Transitions

**State diagram:**
```
┌─────────┐     ┌─────────────┐
│ pending │────▶│ processing  │
└─────────┘     └─────────────┘
                     │     │
                     ▼     ▼
              ┌──────────┐ ┌────────┐
              │completed │ │ failed │
              └──────────┘ └────────┘
```

**Validation check in payout processor:**

```python
# From payouts/tasks.py - process_payout_sync()
def process_payout_sync(payout_id):
    payout = Payout.objects.get(id=payout_id)

    if payout.status != 'pending':
        return  # BLOCKED: Cannot process non-pending payouts

    payout.status = 'processing'
    payout.attempt_count += 1
    payout.save()

    result = simulate_bank_settlement()

    if result == 'success':
        payout.status = 'completed'    # Valid: processing -> completed
    elif result == 'processing':
        payout.status = 'pending'    # Goes back to pending for retry
    else:
        payout.status = 'failed'     # Valid: processing -> failed
        PayoutService.return_funds(payout)  # Atomically return funds
```

**This check (`if payout.status != 'pending'`) blocks:**
- `completed` → any state (including back to `pending` or `processing`)
- `failed` → `completed` (re-completing a failed payout)
- Any backward transition

The state machine is enforced at the worker level - transitions only happen within the allowed set.

---

## 5. AI Audit - Where AI Wrote Wrong Code

**Example 1: Typo in Celery task (process_payout)**

AI originally wrote:
```python
@shared_task(binf=True, max_retries=3)  # "binf" should be "bind"
def process_payout(self, payout_id):
    payout = Payout.object.get(id=payout_id)  # "object" should be "objects"
    payout.attempt_coumt +=1  # "attempt_coumt" should be "attempt_count"
```

I caught these typos and corrected them:
```python
@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    payout = Payout.objects.get(id=payout_id)
    payout.attempt_count += 1
```

**Example 2: Aggregation bug in balance calculation**

AI might have suggested fetching all entries and summing in Python:
```python
# WRONG - not atomic, can cause race conditions
entries = LedgerEntry.objects.filter(merchant=merchant)
balance = sum(e.amount_paise if e.entry_type == 'credit' else -e.amount_paise for e in entries)
```

I caught this and used database-level aggregation instead:
```python
# CORRECT - atomic, single query
result = LedgerEntry.objects.filter(merchant_id=merchant_id).aggregate(
    balance=Sum(Case(When(entry_type='credit', then=F('amount_paise')),
                     When(entry_type='debit', then=-F('amount_paise')), default=0))
)
```

**Example 3: Missing transaction atomicity**

AI might have suggested:
```python
# WRONG - not atomic
balance = LedgerService.calculate_balance(merchant_id)
if balance >= amount:
    Payout.objects.create(...)
    LedgerService.create_entry(...)
```

I wrapped it in `@transaction.atomic` with row-level locking:
```python
# CORRECT - atomic with lock
@transaction.atomic
def create_payout(merchant_id, ...):
    merchant = Merchant.objects.select_for_update(nowait=True).get(id=merchant_id)
    balance = LedgerService.calculate_balance(merchant_id)
    if balance < amount:
        raise InsufficientFundsError(...)
    # ... rest of creation
```

---

## Bonus Features Implemented

### 1. Docker Compose (docker-compose.yml)

Full containerized setup with PostgreSQL, Redis, Django, and Celery:

```yaml
services:
  db:
    image: postgres:15-alpine
  redis:
    image: redis:7-alpine
  web:
    build: ./backend
    command: gunicorn --bind 0.0.0.0:8000 playto.wsgi:application
  celery:
    build: ./backend
    command: celery -A playto worker --loglevel=info
```

### 2. Inter-Merchant Transfers (transfers app)

Transfer funds between merchant accounts atomically:

```python
@transaction.atomic
def create_transfer(from_merchant, to_merchant_email, amount_paise):
    # Lock both merchants
    from_m = Merchant.objects.select_for_update(nowait=True).get(id=from_merchant.id)
    to_m = Merchant.objects.select_for_update(nowait=True).get(id=to_merchant.id)

    # Create debit + credit entries atomically
    LedgerService.create_entry(from_merchant.id, 'debit', amount_paise, ...)
    LedgerService.create_entry(to_merchant.id, 'credit', amount_paise, ...)
```

API: `POST /api/v1/transfers` with `{ to_merchant_email, amount_paise }`