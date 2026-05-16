import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
}

export default function MetricCard({ title, value, subtitle, icon: Icon, trend }: MetricCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col gap-4">
      <div className="flex items-center justify-between text-gray-400">
        <h3 className="text-sm font-medium">{title}</h3>
        <Icon className="w-5 h-5 text-gray-500" />
      </div>
      <div>
        <p className="text-2xl font-bold text-white">{value}</p>
        {subtitle && (
          <p className={`text-xs mt-1 ${
            trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-500'
          }`}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}
