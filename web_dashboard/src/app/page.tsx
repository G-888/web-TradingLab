"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Globe, Zap, AlertTriangle, ShieldCheck } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function OverviewPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const h = await api.getHealth();
      setHealth(h);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Trading Command Center</h2>
          <p className="text-muted-foreground mt-1 flex items-center gap-2">
            Observation Mode <Badge variant="secondary">Read-Only</Badge>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <ShieldCheck className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">Online</div>
            <p className="text-xs text-muted-foreground mt-1">API & Database Connected</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Live Execution</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-500">Disabled</div>
            <p className="text-xs text-muted-foreground mt-1">Observation mode active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Forward Tests</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">Active</div>
            <p className="text-xs text-muted-foreground mt-1">Logging virtual signals</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Agent</CardTitle>
            <Zap className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Available</div>
            <p className="text-xs text-muted-foreground mt-1">Models ready for analysis</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Globe className="h-5 w-5" /> Market Analysis</CardTitle>
            <CardDescription>Deep-dive technical bias and scenario generation.</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/market-analysis">
              <Button className="w-full">Analyze Markets</Button>
            </Link>
          </CardContent>
        </Card>
        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Activity className="h-5 w-5" /> Strategy Analysis</CardTitle>
            <CardDescription>Compare algorithmic performance side-by-side.</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/strategies">
              <Button className="w-full" variant="outline">View Strategies</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
