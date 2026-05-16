"use client";

import { useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Activity, Target, AlignLeft, RefreshCw } from 'lucide-react';
import StatusBadge from '@/components/dashboard/StatusBadge';

import CandlestickChart from '@/components/charts/CandlestickChart';

export default function MarketAnalysisPage() {
  const [symbol, setSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('H1');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  
  // Chart state
  const [candles, setCandles] = useState<any[]>([]);
  const [loadingChart, setLoadingChart] = useState(false);
  const [chartError, setChartError] = useState<string | null>(null);

  const fetchAnalysis = async () => {
    setLoading(true);
    setLoadingChart(true);
    setChartError(null);
    try {
      const [analysisResult, candlesResult] = await Promise.all([
        api.getMarketAnalysis({ symbol, timeframe }),
        api.getCandles(symbol, timeframe, 300)
      ]);
      setAnalysis(analysisResult);
      if (candlesResult && Array.isArray(candlesResult)) {
         setCandles(candlesResult);
      } else {
         setCandles([]);
         setChartError("Failed to fetch candle data.");
      }
    } catch (e) {
      console.error("Failed to fetch analysis", e);
      setChartError("Failed to load chart data.");
    } finally {
      setLoading(false);
      setLoadingChart(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Market Analysis Center</h2>
          <p className="text-muted-foreground mt-1">Deep-dive technical assessment and strategy outlook.</p>
        </div>
      </div>

      <Card>
        <CardHeader className="bg-muted/30 border-b pb-4">
          <div className="flex flex-wrap items-end gap-4">
            <div className="space-y-1.5 w-48">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Symbol</label>
              <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select symbol" />
                </SelectTrigger>
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
            <div className="space-y-1.5 w-32">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Timeframe</label>
              <Select value={timeframe} onValueChange={(val) => val && setTimeframe(val)}>
                <SelectTrigger>
                  <SelectValue placeholder="Timeframe" />
                </SelectTrigger>
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
            <Button onClick={fetchAnalysis} disabled={loading} className="gap-2">
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Analyzing...' : 'Analyze Market'}
            </Button>
          </div>
        </CardHeader>
      </Card>
      
      {/* Chart Section */}
      <Card>
        <CardContent className="p-4">
          <CandlestickChart 
            candles={candles} 
            loading={loadingChart} 
            error={chartError} 
            height={420} 
          />
        </CardContent>
      </Card>

      {analysis && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-1 space-y-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  Market Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Overall Bias</p>
                    <StatusBadge status={analysis.bias} />
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Confidence</p>
                    <div className="flex items-center gap-2">
                      <span className="font-bold">{analysis.confidence}%</span>
                      <Progress value={analysis.confidence} className="h-1.5 w-16" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Regime</p>
                    <Badge variant="outline">{analysis.regime}</Badge>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Volatility</p>
                    <span className="font-medium">{analysis.volatility}</span>
                  </div>
                </div>
                <div className="pt-4 border-t">
                  <p className="text-sm leading-relaxed">{analysis.summary}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="h-5 w-5 text-primary" />
                  Key Levels
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysis.key_levels?.map((lvl: any, i: number) => (
                    <div key={i} className="flex justify-between items-center text-sm p-2 bg-muted/40 rounded-md border">
                      <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${lvl.type === 'Resistance' ? 'bg-red-500' : lvl.type === 'Support' ? 'bg-green-500' : 'bg-blue-500'}`} />
                        <span className="font-medium text-muted-foreground">{lvl.type}</span>
                      </div>
                      <span className="font-mono font-bold">{lvl.price.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="xl:col-span-2 space-y-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <AlignLeft className="h-5 w-5 text-primary" />
                  Strategy Votes
                </CardTitle>
                <CardDescription>Consensus across multiple AI and technical strategy modules.</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Strategy</TableHead>
                      <TableHead>Vote</TableHead>
                      <TableHead>Confidence</TableHead>
                      <TableHead>Reasoning</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {analysis.strategy_votes?.map((vote: any, i: number) => (
                      <TableRow key={i}>
                        <TableCell className="font-medium">{vote.strategy}</TableCell>
                        <TableCell><StatusBadge status={vote.direction} /></TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="text-xs w-6">{vote.confidence}%</span>
                            <Progress value={vote.confidence} className="h-1.5 w-12" />
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">{vote.reason}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
