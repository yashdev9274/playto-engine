# Playto Payout Engine

A minimal payout engine for Indian agencies and freelancers to collect international payments.

## Demo Video



https://github.com/user-attachments/assets/d27c9a0a-8117-4e21-bcaf-a0ee85294200



<video controls width="100%">
  <source src="playto-engine-demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

*[Download demo video](playto-engine-demo.mp4)*

---

## Quick Start

### Option A: Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Seed database (in new terminal)
docker exec playto-web-1 python seed.py
```

**Access:**
- Frontend: http://localhost:3000 (not included in Docker)
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432 (credentials: postgres/postgres)
- Redis: localhost:6379

**Stop:**
```bash
docker-compose down
```

---

### Option B: Local Development

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed database with test merchants
python seed.py

# Run server
python manage.py runserver 8000

# In another terminal - run Celery worker (optional, sync mode works for demo)
celery -A playto worker --loglevel=info
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Login Credentials

| Merchant | Email | API Key |
|----------|-------|---------|
| Acme Agency | acme@example.com | 1b5e0f08f07ff0aeba3348503730e0870bd01ae8f31c3cdc3ef53b264a4ad23a |
| TechFreelancer | tech@example.com | aac0345ce7bb1afad00383659f49257056ef6deb668ffe3ca2ec0e2e3cd70418 |
| Design Studio | design@example.com | 077043f1b6fdbc0edc621ac7ebac96228d0637fd334dfd33f3f7f704a5f5e47b |

## API Endpoints

| Method | Endpoint | Description |
|--------|-----------|--------------|
| GET | `/api/v1/merchants/me/balance` | Get merchant balance |
| GET | `/api/v1/merchants/me/ledger` | Get transaction history |
| POST | `/api/v1/merchants/me/ledger/add-funds` | Add funds (credit) |
| GET | `/api/v1/payouts` | List payouts |
| POST | `/api/v1/payouts` | Create payout |

## Tech Stack

- **Backend**: Django + DRF (Python)
- **Frontend**: Next.js 14 + Tailwind CSS
- **Database**: PostgreSQL (SQLite for dev)
- **Background Jobs**: Celery

## Features

- Paise-based integer balance (no floats)
- Idempotent payout requests with UUID keys
- Concurrent payout protection with SELECT FOR UPDATE
- Automatic fund return on payout failure
- State machine for payout lifecycle

## Tests

```bash
# Run concurrency test
python -m pytest tests/test_concurrency.py -v

# Run idempotency test
python -m pytest tests/test_idempotency.py -v
```
