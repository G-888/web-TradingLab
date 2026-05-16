"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, AlertTriangle } from 'lucide-react';
import StatusBadge from '@/components/dashboard/StatusBadge';

import TradingViewWidget from '@/components/charts/TradingViewWidget';

export default function MarketOutlookPage() {
  const [symbol, setSymbol] = useState('XAUUSD');
  const [outlook, setOutlook] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await api.getMarketOutlook(symbol);
      if (data) setOutlook(data);
      setLoading(false);
    }
    load();
  }, [symbol]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Market Outlook Center</h2>
          <p className="text-muted-foreground mt-1">Human-readable market bias and scenario planning.</p>
        </div>
        <div className="w-48">
          <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
            <SelectTrigger><SelectValue placeholder="Select symbol" /></SelectTrigger>
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
      </div>

      <Card>
        <CardContent className="p-0 overflow-hidden rounded-md border-0">
          <TradingViewWidget symbol={symbol} />
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center p-12 text-muted-foreground">Generating outlook...</div>
      ) : outlook ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
             <Card>
               <CardHeader>
                 <CardTitle className="flex items-center gap-2"><LineChart className="h-5 w-5 text-primary" /> Current Bias</CardTitle>
               </CardHeader>
               <CardContent className="space-y-4">
                 <div className="grid grid-cols-2 gap-4">
                   <div>
                     <p className="text-sm text-muted-foreground">Intraday Bias</p>
                     <StatusBadge status={outlook.intraday_bias} />
                   </div>
                   <div>
                     <p className="text-sm text-muted-foreground">Swing Bias</p>
                     <StatusBadge status={outlook.swing_bias} />
                   </div>
                   <div>
                     <p className="text-sm text-muted-foreground">Market Regime</p>
                     <Badge variant="outline">{outlook.regime}</Badge>
                   </div>
                   <div>
                     <p className="text-sm text-muted-foreground">Volatility</p>
                     <span className="font-bold">{outlook.volatility}</span>
                   </div>
                 </div>
               </CardContent>
             </Card>

             <Card className="border-red-900/50 bg-red-950/10">
               <CardHeader>
                 <CardTitle className="text-red-500 flex items-center gap-2">
                   <AlertTriangle className="h-5 w-5" /> Risk Notes
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <ul className="list-disc pl-5 space-y-2 text-sm text-red-400">
                   {outlook.risk_notes.map((note: string, i: number) => (
                     <li key={i}>{note}</li>
                   ))}
                 </ul>
               </CardContent>
             </Card>
          </div>

          <div className="lg:col-span-2 space-y-6">
             <Card>
               <CardHeader>
                 <CardTitle>Scenario Planning</CardTitle>
                 <CardDescription>AI-generated projections based on current technical structure.</CardDescription>
               </CardHeader>
               <CardContent className="space-y-6">
                 <div className="space-y-2">
                   <h4 className="font-semibold text-green-500 flex items-center gap-2">Bullish Scenario</h4>
                   <p className="text-sm text-muted-foreground bg-muted/30 p-3 rounded-md">{outlook.bullish_scenario}</p>
                 </div>
                 <div className="space-y-2">
                   <h4 className="font-semibold text-red-500 flex items-center gap-2">Bearish Scenario</h4>
                   <p className="text-sm text-muted-foreground bg-muted/30 p-3 rounded-md">{outlook.bearish_scenario}</p>
                 </div>
                 <div className="space-y-2">
                   <h4 className="font-semibold text-blue-500 flex items-center gap-2">Neutral Scenario</h4>
                   <p className="text-sm text-muted-foreground bg-muted/30 p-3 rounded-md">{outlook.neutral_scenario}</p>
                 </div>
               </CardContent>
             </Card>
          </div>
        </div>
      ) : (
        <div className="text-center p-12 text-muted-foreground">No outlook data available.</div>
      )}
    </div>
  );
}
