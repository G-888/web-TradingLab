"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Activity, Play, Square, ShieldAlert, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';
import EmptyState from '@/components/dashboard/EmptyState';

export default function ForwardTestsPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [symbol, setSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('H1');
  const [strategies, setStrategies] = useState<any[]>([]);
  const [selectedStrats, setSelectedStrats] = useState<string[]>([]);

  useEffect(() => {
    fetchSessions();
    fetchStrategies();
    fetchReport();
  }, []);

  const fetchStrategies = async () => {
    const strats = await api.getEnabledStrategies();
    // Only forward-testable (can_backtest implies can_forward_test based on our registry update)
    if (strats) {
      setStrategies(strats);
    }
  };

  const fetchSessions = async () => {
    setLoading(true);
    const data = await api.getForwardTestSessions();
    if (data) setSessions(data);
    setLoading(false);
  };

  const fetchReport = async () => {
    const res = await fetch('/api/forward-tests/report');
    if (res.ok) {
      const data = await res.json();
      setReport(data);
    }
  };

  const handleStart = async () => {
    if (selectedStrats.length === 0) return alert('Select at least one strategy.');
    const res = await fetch('/api/forward-tests/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, timeframe, strategies: selectedStrats })
    });
    if (res.ok) {
      fetchSessions();
      fetchReport();
    } else {
      const err = await res.json();
      alert(err.detail || 'Failed to start session.');
    }
  };

  const handleStop = async (id: number) => {
    await fetch(`/api/forward-tests/stop?session_id=${id}`, { method: 'POST' });
    fetchSessions();
    fetchReport();
  };

  const toggleStrat = (id: string) => {
    setSelectedStrats(prev => prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center bg-yellow-950/20 p-4 rounded-xl border border-yellow-900/50">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            Forward Testing Engine
            <Badge variant="destructive" className="uppercase tracking-widest bg-red-600">PAPER TEST ONLY</Badge>
          </h2>
          <p className="text-muted-foreground mt-1 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            LIVE TRADING DISABLED. NO BROKER EXECUTION.
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Virtual Trades</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.total_virtual_trades || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Trades</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.open_trades || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.win_rate || 0}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Virtual PnL</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.virtual_pnl || 0}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-blue-900/50 bg-blue-950/10">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-blue-500" />
            Start Observation Session
          </CardTitle>
          <CardDescription>
            Begin logging virtual signals generated by strategies. Validated against live market data. No execution.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-start gap-4">
            <div className="space-y-1.5 w-48">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Symbol</label>
              <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
                <SelectTrigger><SelectValue placeholder="Symbol" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="XAUUSD">XAUUSD</SelectItem>
                  <SelectItem value="NQ100">NQ100</SelectItem>
                  <SelectItem value="EURUSD">EURUSD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-1.5 w-32">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Timeframe</label>
              <Select value={timeframe} onValueChange={(val) => val && setTimeframe(val)}>
                <SelectTrigger><SelectValue placeholder="Timeframe" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="M15">M15</SelectItem>
                  <SelectItem value="H1">H1</SelectItem>
                  <SelectItem value="H4">H4</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2 flex-1 min-w-[200px] border p-3 rounded-md bg-background/50">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-2">Strategies (Multi-Select)</label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {strategies.map(s => (
                  <div key={s.id} className="flex items-center space-x-2">
                    <input 
                      type="checkbox" 
                      id={s.id} 
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      checked={selectedStrats.includes(s.id)} 
                      onChange={() => toggleStrat(s.id)} 
                    />
                    <label htmlFor={s.id} className="text-sm leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      {s.name}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <Button onClick={handleStart} className="gap-2 h-10 mt-6" disabled={selectedStrats.length === 0}>
              <Play className="h-4 w-4" /> Start Session
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Active & Historical Sessions
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
             <div className="p-8 text-center text-muted-foreground">Loading sessions...</div>
           ) : sessions.length === 0 ? (
             <div className="p-8"><EmptyState message="No forward test sessions running." /></div>
           ) : (
             <Table>
               <TableHeader>
                 <TableRow>
                   <TableHead>Session ID</TableHead>
                   <TableHead>Symbol / TF</TableHead>
                   <TableHead>Strategies</TableHead>
                   <TableHead>Started</TableHead>
                   <TableHead>Status</TableHead>
                   <TableHead className="text-right">Actions</TableHead>
                 </TableRow>
               </TableHeader>
               <TableBody>
                 {sessions.map((session, i) => {
                   let strats = [];
                   try { strats = JSON.parse(session.strategies_json); } catch(e){}
                   return (
                   <TableRow key={i}>
                     <TableCell className="font-mono text-muted-foreground">#{session.id}</TableCell>
                     <TableCell className="font-bold">{session.symbol} <Badge variant="outline" className="ml-2">{session.timeframe}</Badge></TableCell>
                     <TableCell>
                       <div className="flex flex-wrap gap-1">
                         {strats.map((s: string) => <Badge key={s} variant="secondary" className="text-[10px]">{s}</Badge>)}
                       </div>
                     </TableCell>
                     <TableCell className="text-muted-foreground">{session.started_at?.split(' ')[0]}</TableCell>
                     <TableCell>
                        {session.status === 'PENDING_MONITORING' ? (
                          <Badge className="bg-yellow-500 hover:bg-yellow-600 text-black">PENDING MONITORING</Badge>
                        ) : session.status === 'ACTIVE' ? (
                          <Badge className="bg-green-500 hover:bg-green-600 animate-pulse">RECORDING</Badge>
                        ) : (
                          <Badge variant="secondary">STOPPED</Badge>
                        )}
                     </TableCell>
                     <TableCell className="text-right">
                        {(session.status === 'ACTIVE' || session.status === 'PENDING_MONITORING') && (
                          <Button variant="destructive" size="sm" onClick={() => handleStop(session.id)} className="gap-1 h-8">
                            <Square className="h-3 w-3" /> Stop
                          </Button>
                        )}
                     </TableCell>
                   </TableRow>
                 )})}
               </TableBody>
             </Table>
           )}
        </CardContent>
      </Card>
    </div>
  );
}
