import { BadgeInfo } from 'lucide-react';

export default function Header() {
  return (
    <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6 shrink-0 text-white">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-full border border-gray-700">
          <BadgeInfo className="w-4 h-4 text-blue-400" />
          <span className="text-gray-300">Local Environment</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-gray-400 text-sm font-medium">System Online</span>
        </div>
      </div>
    </header>
  );
}
