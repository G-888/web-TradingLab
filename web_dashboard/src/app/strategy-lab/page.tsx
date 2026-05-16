"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Activity, Play, CheckCircle2, CircleDashed, AlertTriangle, ShieldAlert, BarChart2, TrendingUp, TrendingDown, Target } from 'lucide-react';

export default function StrategyLabPage() {
  const [symbol, setSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('H1');
  const [lookback, setLookback] = useState('90d');
  
  const [testableStrategies, setTestableStrategies] = useState<any[]>([]);
  const [rankings, setRankings] = useState<any[]>([]);
  const [compareData, setCompareData] = useState<any>(null);
  
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  
  const [testTypeTab, setTestTypeTab] = useState('backtest');

  useEffect(() => {
    loadData();
  }, [symbol, timeframe, testTypeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [testable, rank, cmp] = await Promise.all([
        api.getStrategyLabTestable(testTypeTab),
        api.getStrategyLabRankings(symbol, timeframe),
        api.getStrategyLabCompare(symbol, timeframe)
      ]);
      if (testable) setTestableStrategies(testable);
      if (rank) setRankings(rank);
      if (cmp && cmp.status === 'success') setCompareData(cmp);
      else setCompareData(null);
    } catch (e) {
      console.error("Failed to load strategy lab data", e);
    }
    setLoading(false);
  };

  const handleBacktestAll = async () => {
    setActionLoading(true);
    const res = await api.runStrategyLabBacktestAll({
      symbol, timeframe, lookback, strategies: ['all']
    });
    if (res && res.status === 'success') {
      await loadData();
      alert(`Batch Backtest Started. Processed ${res.processed} out of ${res.total} strategies.`);
    } else {
      alert(res?.message || "Error running backtest all.");
    }
    setActionLoading(false);
  };

  const handleForwardTestStart = async () => {
    setActionLoading(true);
    const res = await api.startStrategyLabForwardTest({
      symbol, timeframe, duration_days: 30, strategies: ['all']
    });
    if (res && res.status === 'success') {
      alert(`Forward Test Session Started for ${res.started_sessions.length} strategies.\n\nPAPER TEST ONLY.`);
    } else {
      alert(res?.message || "Error starting forward test.");
    }
    setActionLoading(false);
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Strategy Lab</h2>
        <p className="text-muted-foreground mt-1">Systematically backtest, forward test, compare, and rank strategies safely.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Alert variant="destructive" className="md:col-span-4 bg-red-900/10 border-red-900/50">
          <ShieldAlert className="h-4 w-4" />
          <AlertTitle>Safety Labels</AlertTitle>
          <AlertDescription className="flex gap-2 mt-2 flex-wrap">
            <Badge variant="destructive">BACKTEST ONLY</Badge>
            <Badge variant="destructive">PAPER TEST ONLY</Badge>
            <Badge variant="outline" className="text-red-500 border-red-500/50">LIVE TRADING DISABLED</Badge>
            <Badge variant="outline" className="text-red-500 border-red-500/50">NOT FINANCIAL ADVICE</Badge>
          </AlertDescription>
        </Alert>
      </div>

      {/* Control Panel */}
      <Card>
        <CardContent className="p-4 flex flex-wrap gap-4 items-center bg-muted/20">
          <div className="w-32">
            <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
              <SelectTrigger><SelectValue placeholder="Symbol" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="XAUUSD">XAUUSD</SelectItem>
                <SelectItem value="NQ100">NQ100</SelectItem>
                <SelectItem value="EURUSD">EURUSD</SelectItem>
                <SelectItem value="BTCUSD">BTCUSD</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="w-32">
            <Select value={timeframe} onValueChange={(val) => val && setTimeframe(val)}>
              <SelectTrigger><SelectValue placeholder="Timeframe" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="M15">M15</SelectItem>
                <SelectItem value="H1">H1</SelectItem>
                <SelectItem value="H4">H4</SelectItem>
                <SelectItem value="D1">D1</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="w-32">
            <Select value={lookback} onValueChange={(val) => val && setLookback(val)}>
              <SelectTrigger><SelectValue placeholder="Lookback" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="30d">30 Days</SelectItem>
                <SelectItem value="90d">90 Days</SelectItem>
                <SelectItem value="180d">180 Days</SelectItem>
                <SelectItem value="1y">1 Year</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex-1 flex justify-end gap-2">
            <Button variant="default" onClick={handleBacktestAll} disabled={actionLoading || loading}>
              <Activity className="w-4 h-4 mr-2" /> Backtest All
            </Button>
            <Button variant="secondary" onClick={handleForwardTestStart} disabled={actionLoading || loading}>
              <Play className="w-4 h-4 mr-2" /> Start Forward Tests
            </Button>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="rankings" className="space-y-6">
        <TabsList>
          <TabsTrigger value="rankings">Ranking Board</TabsTrigger>
          <TabsTrigger value="testability">Testability Map</TabsTrigger>
        </TabsList>

        <TabsContent value="rankings" className="space-y-6">
          {compareData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-primary/5 border-primary/20">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Target className="w-4 h-4"/> Best Overall Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{compareData.best_by_score?.strategy_name}</div>
                  <p className="text-xs text-muted-foreground mt-1">Score: {compareData.best_by_score?.score}</p>
                </CardContent>
              </Card>

              <Card className="bg-green-500/5 border-green-500/20">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-500"/> Highest Win Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{compareData.best_by_win_rate?.strategy_name}</div>
                  <p className="text-xs text-muted-foreground mt-1">Win Rate: {(compareData.best_by_win_rate?.win_rate * 100).toFixed(1)}%</p>
                </CardContent>
              </Card>

              <Card className="bg-blue-500/5 border-blue-500/20">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-blue-500"/> Best Profit Factor
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{compareData.best_by_profit_factor?.strategy_name}</div>
                  <p className="text-xs text-muted-foreground mt-1">PF: {compareData.best_by_profit_factor?.profit_factor}</p>
                </CardContent>
              </Card>

              <Card className="bg-yellow-500/5 border-yellow-500/20">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <TrendingDown className="w-4 h-4 text-yellow-500"/> Most Consistent (Low DD)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{compareData.most_consistent?.strategy_name}</div>
                  <p className="text-xs text-muted-foreground mt-1">Max DD: {compareData.most_consistent?.max_drawdown}%</p>
                </CardContent>
              </Card>

              {compareData.warnings && compareData.warnings.length > 0 && (
                <div className="md:col-span-4 mt-2">
                  <Alert className="bg-yellow-500/10 border-yellow-500/20 text-yellow-500">
                    <AlertTriangle className="h-4 w-4" color="#eab308" />
                    <AlertTitle>Benchmark Warnings</AlertTitle>
                    <AlertDescription>
                      <ul className="list-disc pl-5 mt-2 space-y-1">
                        {compareData.warnings.map((w: string, i: number) => <li key={i}>{w}</li>)}
                      </ul>
                    </AlertDescription>
                  </Alert>
                </div>
              )}
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Strategy Rankings</CardTitle>
              <CardDescription>Ranked by transparent edge scoring formula.</CardDescription>
            </CardHeader>
            <CardContent>
              {rankings.length === 0 ? (
                <div className="text-center py-10 text-muted-foreground">
                  No benchmark results yet. Run a backtest to compare strategies.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Rank</TableHead>
                      <TableHead>Strategy</TableHead>
                      <TableHead>Trades</TableHead>
                      <TableHead>Win Rate</TableHead>
                      <TableHead>Profit Factor</TableHead>
                      <TableHead>Max DD</TableHead>
                      <TableHead>Expectancy</TableHead>
                      <TableHead className="text-right">Score</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rankings.map((r, i) => (
                      <TableRow key={r.id}>
                        <TableCell className="font-medium">#{i + 1}</TableCell>
                        <TableCell>{r.strategy_name}</TableCell>
                        <TableCell>{r.total_trades}</TableCell>
                        <TableCell>{(r.win_rate * 100).toFixed(1)}%</TableCell>
                        <TableCell>{r.profit_factor}</TableCell>
                        <TableCell className="text-red-500">{r.max_drawdown}%</TableCell>
                        <TableCell>{r.expectancy}</TableCell>
                        <TableCell className="text-right font-bold text-primary">{r.score}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="testability" className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Testability Matrix</CardTitle>
                <CardDescription>Shows which strategies have executable logic adapters mapped.</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant={testTypeTab === 'backtest' ? 'default' : 'outline'} size="sm" onClick={() => setTestTypeTab('backtest')}>Backtest</Button>
                <Button variant={testTypeTab === 'forward_test' ? 'default' : 'outline'} size="sm" onClick={() => setTestTypeTab('forward_test')}>Forward Test</Button>
                <Button variant={testTypeTab === 'analysis' ? 'default' : 'outline'} size="sm" onClick={() => setTestTypeTab('analysis')}>Analysis</Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Strategy</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Can Analyze</TableHead>
                    <TableHead>Can Backtest</TableHead>
                    <TableHead>Can Forward Test</TableHead>
                    <TableHead>Reason</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {testableStrategies.map((s) => {
                    const test = s.testability || {};
                    return (
                      <TableRow key={s.id}>
                        <TableCell className="font-medium">{s.name}</TableCell>
                        <TableCell><Badge variant="outline">{s.status}</Badge></TableCell>
                        <TableCell>{test.can_analyze ? <CheckCircle2 className="w-4 h-4 text-green-500"/> : <CircleDashed className="w-4 h-4 text-muted-foreground"/>}</TableCell>
                        <TableCell>{test.can_backtest ? <CheckCircle2 className="w-4 h-4 text-green-500"/> : <CircleDashed className="w-4 h-4 text-muted-foreground"/>}</TableCell>
                        <TableCell>{test.can_forward_test ? <CheckCircle2 className="w-4 h-4 text-green-500"/> : <CircleDashed className="w-4 h-4 text-muted-foreground"/>}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{test.reason}</TableCell>
                      </TableRow>
                    )
                  })}
                  {testableStrategies.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-4 text-muted-foreground">No testable strategies found for this mode.</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
