'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { ArrowRightLeft, Loader2 } from 'lucide-react';

interface TransferFormProps {
  token: string;
  onTransferComplete: () => void;
}

export default function TransferForm({ token, onTransferComplete }: TransferFormProps) {
  const [email, setEmail] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.transfer(token, email, parseInt(amount) * 100);
      setSuccess('Transfer successful!');
      setEmail('');
      setAmount('');
      onTransferComplete();
    } catch (err: any) {
      setError(err.message || 'Transfer failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleTransfer} className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center gap-2 mb-4">
        <ArrowRightLeft className="w-5 h-5 text-red-600" />
        <h2 className="text-lg font-semibold">Transfer Funds</h2>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-sm">{error}</div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded text-sm">{success}</div>
      )}

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Recipient Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 text-black rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
          placeholder="tech@example.com"
          required
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Amount (INR)
        </label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 text-black rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
          placeholder="500"
          min="1"
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-red-600 text-white py-2.5 rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing...
          </>
        ) : (
          'Transfer Funds'
        )}
      </button>
    </form>
  );
}