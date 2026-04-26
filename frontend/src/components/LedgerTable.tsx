import { LedgerEntry } from '@/types';

interface LedgerTableProps {
  entries: LedgerEntry[];
}

export default function LedgerTable({ entries }: LedgerTableProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
      <table className="min-w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.id} className="border-t border-gray-100 hover:bg-gray-50">
              <td className="px-4 py-3 text-sm text-gray-600">
                {new Date(entry.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    entry.entry_type === 'credit'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {entry.entry_type}
                </span>
              </td>
              <td className="px-4 py-3 text-sm font-mono font-medium">
                <span className={entry.entry_type === 'credit' ? 'text-green-600' : 'text-red-600'}>
                  {entry.entry_type === 'credit' ? '+' : '-'}₹{((entry.amount_paise) / 100).toFixed(2)}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-500">{entry.description || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {entries.length === 0 && (
        <div className="text-center py-8 text-gray-500">No transactions yet</div>
      )}
    </div>
  );
}