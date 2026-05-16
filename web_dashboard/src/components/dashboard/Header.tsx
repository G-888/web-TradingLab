"use client";

import { BadgeInfo } from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Badge } from '@/components/ui/badge';

export default function Header() {
  return (
    <header className="h-16 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border flex items-center justify-between px-6 shrink-0 z-50 sticky top-0">
      <h1 className="text-lg font-semibold text-foreground">Terminal Dashboard</h1>
      <div className="flex items-center gap-4">
        <Badge variant="secondary" className="flex items-center gap-2 px-3 py-1 font-normal">
          <BadgeInfo className="w-3.5 h-3.5 text-primary" />
          <span>Local Environment</span>
        </Badge>
        
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
          </span>
          <span className="text-muted-foreground text-xs font-medium">System Online</span>
        </div>
        
        <div className="h-6 w-px bg-border mx-2"></div>
        <ThemeToggle />
      </div>
    </header>
  );
}
