interface BalanceCardProps {
  title: string;
  amount: number;
}

export default function BalanceCard({ title, amount }: BalanceCardProps) {
  const formatted = amount ? (amount / 100).toFixed(2) : '0.00';

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 mt-1">₹{formatted}</p>
      <p className="text-xs text-gray-400 mt-1">{amount || 0} paise</p>
    </div>
  );
}