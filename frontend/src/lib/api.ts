import { Balance, LedgerResponse, Payout, PayoutRequest, Transfer } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new ApiError(response.status, error.error || 'Request failed');
  }
  return response.json();
}

export const api = {
  async getBalance(token: string): Promise<Balance> {
    const response = await fetch(`${API_BASE}/api/v1/merchants/me/balance`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return handleResponse<Balance>(response);
  },

  async getLedger(token: string, params: Record<string, string> = {}): Promise<LedgerResponse> {
    const searchParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE}/api/v1/merchants/me/ledger?${searchParams}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return handleResponse<LedgerResponse>(response);
  },

  async createPayout(token: string, data: PayoutRequest): Promise<Payout> {
    const idempotencyKey = crypto.randomUUID();
    const response = await fetch(`${API_BASE}/api/v1/payouts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Idempotency-Key': idempotencyKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse<Payout>(response);
  },

  async getPayouts(token: string): Promise<Payout[]> {
    const response = await fetch(`${API_BASE}/api/v1/payouts`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return handleResponse<Payout[]>(response);
  },

  async addFunds(token: string, amountPaise: number, description?: string): Promise<{ success: boolean; amount_paise: number; message: string }> {
    const response = await fetch(`${API_BASE}/api/v1/merchants/me/ledger/add-funds`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ amount_paise: amountPaise, description }),
    });
    return handleResponse(response);
  },

  async transfer(token: string, toMerchantEmail: string, amountPaise: number): Promise<Transfer> {
    const response = await fetch(`${API_BASE}/api/v1/transfers`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        to_merchant_email: toMerchantEmail, 
        amount_paise: amountPaise 
      }),
    });
    return handleResponse<Transfer>(response);
  },

  async getTransfers(token: string): Promise<Transfer[]> {
    const response = await fetch(`${API_BASE}/api/v1/transfers`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return handleResponse<Transfer[]>(response);
  },
};