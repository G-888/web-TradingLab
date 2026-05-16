"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import EmptyState from '@/components/dashboard/EmptyState';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Play } from 'lucide-react';

import CandlestickChart, { ChartMarker } from '@/components/charts/CandlestickChart';

export default function BacktestsPage() {
  const [runs, setRuns] = useState<any[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(true);

  // Form State
  const [symbol, setSymbol] = useState('XAUUSD');
  const [strategy, setStrategy] = useState('SMC');
  const [timeframe, setTimeframe] = useState('H1');
  const [lookback, setLookback] = useState('90d');
  const [capital, setCapital] = useState('10000');
  const [risk, setRisk] = useState('1.0');
  const [running, setRunning] = useState(false);

  // Chart State
  const [candles, setCandles] = useState<any[]>([]);
  const [markers, setMarkers] = useState<ChartMarker[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [loadingChart, setLoadingChart] = useState(false);
  const [chartError, setChartError] = useState<string | null>(null);

  const [strategies, setStrategies] = useState<any[]>([]);

  useEffect(() => {
    fetchRuns();
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    const strats = await api.getEnabledStrategies();
    if (strats) setStrategies(strats);
  };

  const fetchRuns = async () => {
    setLoadingRuns(true);
    const data = await api.getBacktestRuns();
    if (data) setRuns(data);
    setLoadingRuns(false);
  };

  const handleRunBacktest = async () => {
    setRunning(true);
    setLoadingChart(true);
    setChartError(null);
    setMarkers([]);
    setTrades([]);

    try {
      const payload = {
        symbol,
        strategy,
        timeframe,
        lookback,
        initial_capital: parseFloat(capital),
        risk_per_trade: parseFloat(risk)
      };

      const [result, candlesResult] = await Promise.all([
        api.runBacktest(payload),
        api.getCandles(symbol, timeframe, 300)
      ]);

      if (candlesResult && Array.isArray(candlesResult)) {
        setCandles(candlesResult);

        // Real markers are generated below using result.trades
      } else {
        setCandles([]);
        setChartError("Failed to load historical data for chart.");
      }

      if (result) {
        if (result.error || result.detail) {
          setChartError(result.error || result.detail);
        } else if (result.summary) {
          // Generate markers from actual trades
          if (result.trades && result.trades.length > 0) {
            const newMarkers: ChartMarker[] = [];
            result.trades.forEach((trade: any) => {
              const entryUnix = Math.floor(new Date(trade.entry_time + 'Z').getTime() / 1000);
              const exitUnix = Math.floor(new Date(trade.exit_time + 'Z').getTime() / 1000);
              
              newMarkers.push({
                time: entryUnix as any,
                position: trade.direction === 'BUY' ? 'belowBar' : 'aboveBar',
                color: trade.direction === 'BUY' ? '#22C55E' : '#EF4444',
                shape: trade.direction === 'BUY' ? 'arrowUp' : 'arrowDown',
                text: trade.direction
              });
              
              newMarkers.push({
                time: exitUnix as any,
                position: trade.direction === 'BUY' ? 'aboveBar' : 'belowBar',
                color: trade.pnl > 0 ? '#22C55E' : '#EF4444',
                shape: 'circle',
                text: 'EXIT'
              });
            });
            setMarkers(newMarkers);
            setTrades(result.trades);
          } else {
            setTrades([]);
          }

          // Mock appending the run to the list
          const newRun = {
            id: result.run_id,
            strategy: strategy,
            timeframe: timeframe,
            total_trades: result.summary.total_trades,
            win_rate: result.summary.win_rate,
            profit_factor: result.summary.profit_factor,
            max_drawdown: result.summary.max_drawdown,
            total_pnl: result.summary.total_pnl,
            ran_at: new Date().toISOString().split('T')[0]
          };
          setRuns([newRun, ...runs]);
        }
      }
    } catch (e) {
      console.error(e);
      setChartError("Error running backtest visualization.");
    } finally {
      setRunning(false);
      setLoadingChart(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Backtests</h2>
          <p className="text-muted-foreground mt-1">Review strategy performance simulations.</p>
        </div>
      </div>

      <Tabs defaultValue="new" className="space-y-6">
        <TabsList>
          <TabsTrigger value="new">Run Simulation</TabsTrigger>
          <TabsTrigger value="runs">Run History</TabsTrigger>
        </TabsList>
        
        <TabsContent value="new" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configure Backtest</CardTitle>
              <CardDescription>Setup parameters for a historical strategy run.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Symbol</label>
                  <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
                    <SelectTrigger><SelectValue placeholder="Symbol" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="XAUUSD">XAUUSD</SelectItem>
                      <SelectItem value="NQ100">NQ100</SelectItem>
                      <SelectItem value="DJI30">DJI30</SelectItem>
                      <SelectItem value="GBPJPY">GBPJPY</SelectItem>
                      <SelectItem value="USDJPY">USDJPY</SelectItem>
                      <SelectItem value="EURUSD">EURUSD</SelectItem>
                      <SelectItem value="BTCUSD">BTCUSD</SelectItem>
                      <SelectItem value="ETHUSD">ETHUSD</SelectItem>
                      <SelectItem value="USOIL">USOIL</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Strategy</label>
                  <Select value={strategy} onValueChange={(val) => val && setStrategy(val)}>
                    <SelectTrigger><SelectValue placeholder="Strategy" /></SelectTrigger>
                    <SelectContent>
                      {strategies.length > 0 ? (
                        strategies.map(s => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)
                      ) : (
                        <SelectItem value="SMC">SMC</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Timeframe</label>
                  <Select value={timeframe} onValueChange={(val) => val && setTimeframe(val)}>
                    <SelectTrigger><SelectValue placeholder="Timeframe" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="M5">M5</SelectItem>
                      <SelectItem value="M15">M15</SelectItem>
                      <SelectItem value="M30">M30</SelectItem>
                      <SelectItem value="H1">H1</SelectItem>
                      <SelectItem value="H4">H4</SelectItem>
                      <SelectItem value="D1">D1</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Lookback Period</label>
                  <Select value={lookback} onValueChange={(val) => val && setLookback(val)}>
                    <SelectTrigger><SelectValue placeholder="Lookback" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7d">7 Days</SelectItem>
                      <SelectItem value="30d">30 Days</SelectItem>
                      <SelectItem value="90d">90 Days</SelectItem>
                      <SelectItem value="180d">180 Days</SelectItem>
                      <SelectItem value="1y">1 Year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Initial Capital ($)</label>
                  <Input type="number" value={capital} onChange={(e) => setCapital(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Risk Per Trade (%)</label>
                  <Input type="number" step="0.1" value={risk} onChange={(e) => setRisk(e.target.value)} />
                </div>
              </div>
              <div className="mt-8 flex justify-end">
                <Button onClick={handleRunBacktest} disabled={running} className="gap-2">
                  <Play className={`h-4 w-4 ${running ? 'animate-pulse' : ''}`} />
                  {running ? 'Running Simulation...' : 'Run Backtest'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Chart Display Area */}
          {(candles.length > 0 || loadingChart || chartError) && (
            <Card>
              <CardHeader>
                <CardTitle>Visualization</CardTitle>
                <CardDescription>Visualizing recent actual trades from the simulated run.</CardDescription>
              </CardHeader>
              <CardContent className="p-4">
                <CandlestickChart 
                  candles={candles} 
                  markers={markers}
                  loading={loadingChart} 
                  error={chartError} 
                  height={420} 
                />
              </CardContent>
            </Card>
          )}

          {trades.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Trade Log</CardTitle>
                <CardDescription>All executed trades during the simulation.</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Entry Time</TableHead>
                      <TableHead>Exit Time</TableHead>
                      <TableHead>Direction</TableHead>
                      <TableHead>Entry Price</TableHead>
                      <TableHead>Exit Price</TableHead>
                      <TableHead>Result</TableHead>
                      <TableHead className="text-right">PnL (%)</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {trades.map((trade: any, i: number) => (
                      <TableRow key={i}>
                        <TableCell className="text-muted-foreground">{trade.entry_time.split('T').join(' ').split('.')[0]}</TableCell>
                        <TableCell className="text-muted-foreground">{trade.exit_time.split('T').join(' ').split('.')[0]}</TableCell>
                        <TableCell>
                          <Badge variant={trade.direction === 'BUY' ? 'default' : 'destructive'}>{trade.direction}</Badge>
                        </TableCell>
                        <TableCell>{trade.entry_price.toFixed(2)}</TableCell>
                        <TableCell>{trade.exit_price.toFixed(2)}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className={trade.pnl > 0 ? 'text-green-500 border-green-500/20' : trade.pnl < 0 ? 'text-red-500 border-red-500/20' : ''}>
                            {trade.result}
                          </Badge>
                        </TableCell>
                        <TableCell className={`text-right font-mono ${trade.pnl > 0 ? 'text-green-500' : trade.pnl < 0 ? 'text-red-500' : ''}`}>
                          {trade.pnl > 0 ? '+' : ''}{trade.pnl.toFixed(2)}%
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

        </TabsContent>

        <TabsContent value="runs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Historical Runs</CardTitle>
              <CardDescription>A log of all backtest executions and their high-level results.</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              {loadingRuns ? (
                <div className="p-8 text-center text-muted-foreground">Loading runs...</div>
              ) : runs.length === 0 ? (
                <div className="p-8">
                  <EmptyState message="No backtest runs found." />
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Run ID</TableHead>
                      <TableHead>Strategy</TableHead>
                      <TableHead>Timeframe</TableHead>
                      <TableHead>Trades</TableHead>
                      <TableHead>Win Rate</TableHead>
                      <TableHead>PF</TableHead>
                      <TableHead>Max DD</TableHead>
                      <TableHead className="text-right">Total PnL</TableHead>
                      <TableHead className="text-right w-[180px]">Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {runs.map((run: any, i: number) => (
                      <TableRow key={i}>
                        <TableCell className="font-mono text-muted-foreground">#{run.id}</TableCell>
                        <TableCell className="font-medium">{run.strategy}</TableCell>
                        <TableCell><Badge variant="outline">{run.timeframe}</Badge></TableCell>
                        <TableCell>{run.total_trades}</TableCell>
                        <TableCell className={run.win_rate >= 50 ? 'text-green-500 font-medium' : 'text-red-500 font-medium'}>
                          {run.win_rate ? `${run.win_rate.toFixed(1)}%` : '-'}
                        </TableCell>
                        <TableCell className={run.profit_factor >= 1.5 ? 'text-green-500' : ''}>
                          {run.profit_factor ? run.profit_factor.toFixed(2) : '-'}
                        </TableCell>
                        <TableCell className={run.max_drawdown <= -10 ? 'text-red-500' : ''}>
                          {run.max_drawdown ? `${run.max_drawdown.toFixed(1)}%` : '-'}
                        </TableCell>
                        <TableCell className={`text-right font-mono ${run.total_pnl > 0 ? 'text-green-500' : run.total_pnl < 0 ? 'text-red-500' : ''}`}>
                           {run.total_pnl ? run.total_pnl.toFixed(2) : '-'}
                        </TableCell>
                        <TableCell className="text-right text-muted-foreground">{run.ran_at?.split(' ')[0]}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
