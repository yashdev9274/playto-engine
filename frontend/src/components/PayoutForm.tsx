'use client';

import { useState } from 'react';
import { PayoutRequest } from '@/types';

interface PayoutFormProps {
  onSubmit: (data: PayoutRequest) => Promise<void>;
  disabled?: boolean;
}

export default function PayoutForm({ onSubmit, disabled }: PayoutFormProps) {
  const [amount, setAmount] = useState('');
  const [bankAccount, setBankAccount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const amountInPaise = Math.floor(parseFloat(amount) * 100);
    if (isNaN(amountInPaise) || amountInPaise <= 0) {
      setError('Please enter a valid amount');
      setLoading(false);
      return;
    }

    try {
      await onSubmit({
        amount_paise: amountInPaise,
        bank_account_id: bankAccount,
      });
      setAmount('');
      setBankAccount('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payout failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">Request Payout</h2>
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">
          {error}
        </div>
      )}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Amount (INR)</label>
        <input
          type="number"
          step="0.01"
          min="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="w-full px-3 py-2 border text-black border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          placeholder="Enter amount in INR"
          required
          disabled={disabled || loading}
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Bank Account ID</label>
        <input
          type="text"
          value={bankAccount}
          onChange={(e) => setBankAccount(e.target.value)}
          className="w-full px-3 py-2 border text-black border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          placeholder="SBIN0001234"
          required
          disabled={disabled || loading}
        />
      </div>
      <button
        type="submit"
        disabled={loading || disabled}
        className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? 'Processing...' : 'Request Payout'}
      </button>
    </form>
  );
}