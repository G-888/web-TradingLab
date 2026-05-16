"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Globe, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function NewsOutlookPage() {
  const [symbol, setSymbol] = useState('XAUUSD');
  const [news, setNews] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await api.getNewsOutlook(symbol);
      if (data) setNews(data);
      setLoading(false);
    }
    load();
  }, [symbol]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">News Outlook Center</h2>
          <p className="text-muted-foreground mt-1">Track high-impact macroeconomic events.</p>
        </div>
        <div className="w-48">
          <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
            <SelectTrigger><SelectValue placeholder="Select symbol" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="XAUUSD">XAUUSD</SelectItem>
              <SelectItem value="NQ100">NQ100</SelectItem>
              <SelectItem value="BTCUSD">BTCUSD</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {loading ? (
        <div className="text-center p-12 text-muted-foreground">Loading economic calendar...</div>
      ) : news ? (
        <div className="space-y-6">
          <Alert variant="default" className="border-yellow-600/50 bg-yellow-900/10 text-yellow-500">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Warning</AlertTitle>
            <AlertDescription>{news.risk_warning}</AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary" />
                Upcoming High-Impact Events
              </CardTitle>
              <CardDescription>{news.summary}</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Currency</TableHead>
                    <TableHead>Event</TableHead>
                    <TableHead>Impact</TableHead>
                    <TableHead className="text-right">Forecast</TableHead>
                    <TableHead className="text-right">Previous</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {news.high_impact_events.map((ev: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="font-mono text-muted-foreground">{ev.time}</TableCell>
                      <TableCell className="font-bold">{ev.currency}</TableCell>
                      <TableCell>{ev.event}</TableCell>
                      <TableCell>
                        <Badge variant="destructive">{ev.impact}</Badge>
                      </TableCell>
                      <TableCell className="text-right">{ev.forecast}</TableCell>
                      <TableCell className="text-right text-muted-foreground">{ev.previous}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="text-center p-12 text-muted-foreground">No news data available.</div>
      )}
    </div>
  );
}
