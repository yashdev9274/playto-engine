'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Balance, LedgerEntry, Payout, PayoutRequest } from '@/types';
import BalanceCard from '@/components/BalanceCard';
import LedgerTable from '@/components/LedgerTable';
import PayoutForm from '@/components/PayoutForm';
import PayoutHistory from '@/components/PayoutHistory';
import AddFundsForm from '@/components/AddFundsForm';
import TransferForm from '@/components/TransferForm';
import Header from '@/components/Header';

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [merchantName, setMerchantName] = useState('');
  const [balance, setBalance] = useState<Balance>({
    available_balance_paise: 0,
    held_balance_paise: 0,
    total_balance_paise: 0,
  });
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('playto_token');
    const savedName = localStorage.getItem('playto_merchant_name');
    if (savedToken) {
      setToken(savedToken);
      setMerchantName(savedName || 'Merchant');
    } else {
      router.push('/');
    }
  }, [router]);

  const loadData = useCallback(async (authToken: string) => {
    try {
      const [balanceData, ledgerData, payoutsData] = await Promise.all([
        api.getBalance(authToken),
        api.getLedger(authToken),
        api.getPayouts(authToken),
      ]);
      setBalance(balanceData);
      setLedger(ledgerData.results || []);
      setPayouts(payoutsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!token) return;
    loadData(token);
    const interval = setInterval(() => loadData(token), 5000);
    return () => clearInterval(interval);
  }, [token, loadData]);

  const handlePayout = useCallback(
    async (data: PayoutRequest) => {
      if (!token) return;
      await api.createPayout(token, data);
      await loadData(token);
    },
    [token, loadData]
  );

  const handleAddFunds = useCallback(
    async (amountPaise: number, description: string) => {
      if (!token) return;
      await api.addFunds(token, amountPaise, description);
      await loadData(token);
    },
    [token, loadData]
  );

  const handleTransfer = useCallback(async () => {
    if (!token) return;
    await loadData(token);
  }, [token, loadData]);

  const handleLogout = () => {
    localStorage.removeItem('playto_token');
    localStorage.removeItem('playto_merchant_name');
    router.push('/');
  };

  if (loading || !token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header merchantName={merchantName} onLogout={handleLogout} />
      <main className="max-w-6xl mx-auto px-6 py-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Dashboard</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <BalanceCard title="Available Balance" amount={balance.available_balance_paise} />
          <BalanceCard title="Held Balance" amount={balance.held_balance_paise} />
          <BalanceCard title="Total Balance" amount={balance.total_balance_paise} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="grid grid-cols-1 gap-6">
            <PayoutForm onSubmit={handlePayout} />
            <AddFundsForm onAdd={handleAddFunds} />
            <TransferForm token={token || ''} onTransferComplete={handleTransfer} />
          </div>
          <PayoutHistory payouts={payouts} />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Transaction History</h2>
          <LedgerTable entries={ledger} />
        </div>
      </main>
    </div>
  );
}