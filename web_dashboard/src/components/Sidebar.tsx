"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, LineChart, List, Bell, Settings, Activity } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Overview', href: '/', icon: Home },
    { name: 'Signals', href: '/signals', icon: Activity },
    { name: 'Backtests', href: '/backtests', icon: LineChart },
    { name: 'Alerts', href: '/alerts', icon: Bell },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 text-gray-300 flex flex-col h-screen shrink-0">
      <div className="h-16 flex items-center px-6 border-b border-gray-800 font-bold text-lg text-white">
        Gold Bot Dashboard
      </div>
      <nav className="flex-1 py-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                    isActive ? 'bg-gray-800 text-white border-l-4 border-blue-500' : 'hover:bg-gray-800 hover:text-white border-l-4 border-transparent'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
        READ ONLY MODE
      </div>
    </aside>
  );
}
