"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, LineChart, List, Bell, Settings, Activity, BrainCircuit, Microscope, ShieldCheck } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const botItems = [
    { name: 'Signals', href: '/signals', icon: Bell },
    { name: 'Alerts', href: '/alerts', icon: Bell },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const analysisItems = [
    { name: 'Overview', href: '/', icon: Home },
    { name: 'Market Analysis', href: '/market-analysis', icon: LineChart },
    { name: 'Strategy Lab', href: '/strategy-lab', icon: BrainCircuit },
    { name: 'Strategies', href: '/strategies', icon: List },
    { name: 'Backtests', href: '/backtests', icon: Microscope },
    { name: 'Forward Tests', href: '/forward-tests', icon: Activity },
    { name: 'Performance', href: '/performance', icon: ShieldCheck },
    { name: 'Market Outlook', href: '/market-outlook', icon: LineChart },
    { name: 'News Outlook', href: '/news-outlook', icon: Bell },
  ];

  const renderNavGroup = (title: string, items: typeof botItems) => (
    <div className="mb-6">
      <h3 className="px-3 mb-2 text-xs font-bold text-muted-foreground uppercase tracking-wider">
        {title}
      </h3>
      <ul className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <li key={item.name}>
              <Link
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.name}
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col h-screen shrink-0">
      <div className="h-16 flex items-center px-6 border-b border-border font-bold text-lg text-foreground">
        <span className="text-primary mr-2">XAU</span> Gold AI
      </div>
      <nav className="flex-1 py-6 px-4 overflow-y-auto">
        {renderNavGroup("Telegram Bot", botItems)}
        {renderNavGroup("Strategy Lab & Analysis", analysisItems)}
      </nav>
      <div className="p-4 border-t border-border">
        <div className="px-3 py-2 bg-muted rounded-md text-xs font-semibold text-muted-foreground text-center">
          READ ONLY MODE
        </div>
      </div>
    </aside>
  );
}
