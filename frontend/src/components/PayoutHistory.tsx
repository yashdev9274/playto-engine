import { Payout } from '@/types';
import { Clock, CheckCircle, XCircle, Loader2, RotateCcw } from 'lucide-react';

const statusConfig = {
  pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: 'Pending' },
  processing: { color: 'bg-blue-100 text-blue-800', icon: Loader2, label: 'Processing' },
  completed: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Completed' },
  failed: { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Failed' },
};

interface PayoutHistoryProps {
  payouts: Payout[];
}

export default function PayoutHistory({ payouts }: PayoutHistoryProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">Payout History</h2>
      <div className="space-y-3">
        {payouts.map((payout) => {
          const config = statusConfig[payout.status];
          const Icon = config.icon;
          return (
            <div
              key={payout.id}
              className="border-b border-gray-100 pb-3 last:border-b-0 last:pb-0"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-mono text-lg font-semibold text-gray-900">
                    ₹{((payout.amount_paise) / 100).toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-500 font-mono">{payout.bank_account_id}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(payout.created_at).toLocaleString()}
                  </p>
                </div>
                <span
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.color}`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {config.label}
                </span>
              </div>
              {payout.failure_reason && (
                <p className="text-sm text-red-600 mt-2 flex items-center gap-1">
                  <RotateCcw className="w-3 h-3" />
                  {payout.failure_reason}
                </p>
              )}
              {payout.status === 'processing' && payout.attempt_count > 0 && (
                <p className="text-xs text-blue-600 mt-1">Attempt {payout.attempt_count}/3</p>
              )}
            </div>
          );
        })}
        {payouts.length === 0 && (
          <p className="text-gray-500 text-center py-8">No payouts yet</p>
        )}
      </div>
    </div>
  );
}