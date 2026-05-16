"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, TrendingUp, TrendingDown, Target, Zap } from 'lucide-react';
import EmptyState from '@/components/dashboard/EmptyState';

export default function PerformancePage() {
  const [summary, setSummary] = useState<any>(null);
  const [byStrategy, setByStrategy] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [sumData, stratData] = await Promise.all([
        api.getPerformanceSummary(),
        api.getPerformanceByStrategy()
      ]);
      if (sumData) setSummary(sumData);
      if (stratData) setByStrategy(stratData);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Performance Analytics</h2>
        <p className="text-muted-foreground mt-1">Holistic evaluation of strategies and market edges.</p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-muted-foreground">Loading analytics...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Virtual PnL</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-500">${summary?.total_pnl?.toFixed(2)}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary?.win_rate}%</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Profit Factor</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary?.profit_factor}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Max Drawdown</CardTitle>
                <TrendingDown className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-500">-{summary?.max_drawdown}%</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary?.total_trades}</div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Performance by Strategy</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {byStrategy.length === 0 ? (
                <div className="p-8"><EmptyState message="No strategy performance data." /></div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Strategy</TableHead>
                      <TableHead>Win Rate</TableHead>
                      <TableHead className="text-right">Net PnL</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {byStrategy.map((strat, i) => (
                      <TableRow key={i}>
                        <TableCell className="font-medium">{strat.strategy}</TableCell>
                        <TableCell className={strat.win_rate >= 55 ? 'text-green-500 font-medium' : ''}>{strat.win_rate}%</TableCell>
                        <TableCell className={`text-right font-mono ${strat.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          ${strat.pnl.toFixed(2)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
