interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toUpperCase();
  
  let colorClass = 'bg-gray-800 text-gray-300 border-gray-700';
  
  if (normalized === 'BUY' || normalized === 'LONG' || normalized === 'WIN') {
    colorClass = 'bg-green-900/30 text-green-400 border-green-800/50';
  } else if (normalized === 'SELL' || normalized === 'SHORT' || normalized === 'LOSS') {
    colorClass = 'bg-red-900/30 text-red-400 border-red-800/50';
  } else if (normalized === 'ACTIVE') {
    colorClass = 'bg-blue-900/30 text-blue-400 border-blue-800/50';
  }

  return (
    <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${colorClass}`}>
      {normalized}
    </span>
  );
}
