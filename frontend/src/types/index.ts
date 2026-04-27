export interface Merchant {
  id: string;
  name: string;
  email: string;
}

export interface Balance {
  available_balance_paise: number;
  held_balance_paise: number;
  total_balance_paise: number;
}

export interface LedgerEntry {
  id: string;
  entry_type: 'credit' | 'debit';
  amount_paise: number;
  description: string | null;
  reference_id: string | null;
  reference_type: string | null;
  created_at: string;
}

export interface LedgerResponse {
  count: number;
  results: LedgerEntry[];
}

export interface Payout {
  id: string;
  amount_paise: number;
  bank_account_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  attempt_count: number;
  failure_reason: string | null;
  created_at: string;
  processed_at: string | null;
}

export interface PayoutRequest {
  amount_paise: number;
  bank_account_id: string;
}

export interface Transfer {
  id: string;
  from_merchant: string;
  from_merchant_email: string;
  to_merchant: string;
  to_merchant_email: string;
  amount_paise: number;
  status: 'pending' | 'completed' | 'failed';
  failure_reason: string | null;
  created_at: string;
  completed_at: string | null;
}