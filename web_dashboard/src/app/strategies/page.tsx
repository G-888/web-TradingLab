"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Target, Activity, CheckCircle2, CircleDashed, Search, AlertTriangle, CheckSquare, Settings2, BarChart2, BookOpen } from 'lucide-react';
import EmptyState from '@/components/dashboard/EmptyState';
import StatusBadge from '@/components/dashboard/StatusBadge';

export default function StrategiesPage() {
  const [symbol, setSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('H1');
  const [strategies, setStrategies] = useState<any[]>([]);
  const [roadmap, setRoadmap] = useState<any>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Analysis State
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analysisResults, setAnalysisResults] = useState<Record<string, any>>({});

  // Detail Drawer State
  const [selectedStrategy, setSelectedStrategy] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [strats, cats, rmap] = await Promise.all([
        api.getStrategies(),
        api.getStrategyCategories(),
        api.getStrategyRoadmap()
      ]);
      if (strats) setStrategies(strats);
      if (cats) setCategories(cats);
      if (rmap) setRoadmap(rmap);
      setLoading(false);
    }
    load();
  }, []);

  const handleAnalyze = async (strategyId: string) => {
    setAnalyzingId(strategyId);
    const res = await api.analyzeStrategy({ strategy_id: strategyId, symbol, timeframe });
    if (res) {
      setAnalysisResults(prev => ({ ...prev, [strategyId]: res }));
    }
    setAnalyzingId(null);
  };

  const openDetail = async (strategyId: string) => {
    setDrawerOpen(true);
    setDetailLoading(true);
    setSelectedStrategy(null);
    const detail = await api.getStrategyDetail(strategyId);
    if (detail) {
      setSelectedStrategy(detail);
    }
    setDetailLoading(false);
  };

  const filteredStrategies = strategies.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(search.toLowerCase()) || s.description?.toLowerCase().includes(search.toLowerCase());
    const matchesCat = categoryFilter === 'all' || s.category === categoryFilter;
    const matchesStatus = statusFilter === 'all' || s.status === statusFilter;
    return matchesSearch && matchesCat && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'implemented': return <Badge className="bg-green-500/10 text-green-500 border-green-500/20"><CheckCircle2 className="w-3 h-3 mr-1" /> Implemented</Badge>;
      case 'partial': return <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20"><Activity className="w-3 h-3 mr-1" /> Partial</Badge>;
      case 'planned': return <Badge className="bg-gray-500/10 text-gray-500 border-gray-500/20"><CircleDashed className="w-3 h-3 mr-1" /> Planned</Badge>;
      case 'disabled': return <Badge variant="destructive">Disabled</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  const renderStrategyGrid = (list: any[]) => {
    if (loading) return <div className="p-8 text-center text-muted-foreground">Loading strategies...</div>;
    if (list.length === 0) return <EmptyState message="No strategies found matching filters." />;

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {list.map((s) => (
          <Card key={s.id} className="flex flex-col relative overflow-hidden group">
            {s.status === 'planned' && (
              <div className="absolute inset-0 bg-muted/30 z-0 pointer-events-none" />
            )}
            <CardHeader className="pb-2 z-10">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl flex items-center gap-2">
                    {s.name}
                  </CardTitle>
                  <CardDescription className="uppercase tracking-widest text-[10px] font-semibold mt-1 text-primary">
                    {s.category.replace('_', ' ')}
                  </CardDescription>
                </div>
                {getStatusBadge(s.status)}
              </div>
            </CardHeader>
            <CardContent className="flex-1 space-y-4 z-10">
              <p className="text-sm text-muted-foreground line-clamp-2">{s.description}</p>
              
              <div className="flex flex-wrap gap-2">
                 <Badge variant="outline" className="text-xs font-normal">Complex: {s.complexity}</Badge>
                 <Badge variant="outline" className="text-xs font-normal">Risk: {s.risk_level}</Badge>
                 {s.readiness && s.readiness.analysis && (
                   <Badge variant="secondary" className="bg-blue-500/10 text-blue-500 text-[10px] uppercase">Analysis Ready</Badge>
                 )}
              </div>

              {/* Analysis Result Box */}
              {(s.status === 'implemented' || s.status === 'partial') && analysisResults[s.id] && (
                <div className={`p-3 rounded-md border text-sm ${
                  analysisResults[s.id].direction === 'BULLISH' ? 'bg-green-500/10 border-green-500/20 text-green-500' :
                  analysisResults[s.id].direction === 'BEARISH' ? 'bg-red-500/10 border-red-500/20 text-red-500' :
                  'bg-gray-500/10 border-gray-500/20 text-gray-500'
                }`}>
                  <div className="flex justify-between font-bold mb-1">
                    <span>{analysisResults[s.id].direction}</span>
                    <span>{(analysisResults[s.id].confidence || 0).toFixed(1)}%</span>
                  </div>
                  <p className="text-xs opacity-80">{analysisResults[s.id].reason}</p>
                </div>
              )}
            </CardContent>
            <CardFooter className="pt-4 border-t bg-muted/10 gap-2 z-10 flex-col sm:flex-row">
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => openDetail(s.id)}
              >
                <BookOpen className="w-4 h-4 mr-2" /> View Details
              </Button>
              <Button 
                className="w-full"
                disabled={analyzingId === s.id || s.status === 'planned' || s.status === 'disabled'}
                onClick={() => handleAnalyze(s.id)}
              >
                {analyzingId === s.id ? (
                  <><Activity className="w-4 h-4 mr-2 animate-spin" /> Analyzing...</>
                ) : (
                  <><Target className="w-4 h-4 mr-2" /> Analyze Now</>
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    );
  };

  const renderRoadmap = () => {
    if (!roadmap) return <div className="p-8 text-center text-muted-foreground">Loading roadmap...</div>;

    const total = strategies.length;
    const implementedCount = roadmap.implemented?.length || 0;
    const partialCount = roadmap.partial?.length || 0;
    const plannedCount = roadmap.planned?.length || 0;

    return (
      <div className="space-y-8">
        {/* Summary Header */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
           <Card>
             <CardContent className="p-4 flex flex-col items-center justify-center text-center">
               <span className="text-3xl font-bold">{total}</span>
               <span className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Total Strategies</span>
             </CardContent>
           </Card>
           <Card className="bg-green-500/5 border-green-500/20">
             <CardContent className="p-4 flex flex-col items-center justify-center text-center">
               <span className="text-3xl font-bold text-green-500">{implementedCount}</span>
               <span className="text-xs text-green-500/70 uppercase tracking-wider mt-1">Implemented</span>
             </CardContent>
           </Card>
           <Card className="bg-yellow-500/5 border-yellow-500/20">
             <CardContent className="p-4 flex flex-col items-center justify-center text-center">
               <span className="text-3xl font-bold text-yellow-500">{partialCount}</span>
               <span className="text-xs text-yellow-500/70 uppercase tracking-wider mt-1">Partial</span>
             </CardContent>
           </Card>
           <Card className="bg-gray-500/5 border-gray-500/20">
             <CardContent className="p-4 flex flex-col items-center justify-center text-center">
               <span className="text-3xl font-bold text-gray-500">{plannedCount}</span>
               <span className="text-xs text-gray-500/70 uppercase tracking-wider mt-1">Planned</span>
             </CardContent>
           </Card>
        </div>

        {/* Roadmap Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {['implemented', 'partial', 'planned'].map(status => (
            <div key={status} className="space-y-4">
              <h3 className="font-semibold text-lg capitalize flex items-center gap-2 border-b pb-2">
                {getStatusBadge(status)} ({roadmap[status]?.length || 0})
              </h3>
              <div className="space-y-3">
                {roadmap[status]?.map((s: any) => (
                  <Card key={s.id} className="cursor-pointer hover:border-primary transition-colors" onClick={() => openDetail(s.id)}>
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-sm leading-tight">{s.name}</span>
                        {s.recommended_priority === 'high' && <Badge variant="default" className="text-[10px] px-1 py-0 h-4">High Pri</Badge>}
                      </div>
                      <div className="flex items-center gap-2 mt-3">
                        <Badge variant="outline" className="text-[10px] capitalize">{s.category.replace('_', ' ')}</Badge>
                        {status !== 'implemented' && s.next_steps_count > 0 && (
                           <span className="text-xs text-muted-foreground">{s.next_steps_count} steps left</span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
                {(!roadmap[status] || roadmap[status].length === 0) && (
                  <div className="text-sm text-muted-foreground italic text-center py-4">None in this stage</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Strategy Registry</h2>
          <p className="text-muted-foreground mt-1">Explore, manage, and analyze institutional technical strategies.</p>
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid grid-cols-3 w-[400px]">
          <TabsTrigger value="all">All Strategies</TabsTrigger>
          <TabsTrigger value="enabled">Enabled</TabsTrigger>
          <TabsTrigger value="roadmap">Roadmap</TabsTrigger>
        </TabsList>
        
        <TabsContent value="all" className="space-y-6">
          <Card>
            <CardContent className="p-4 flex flex-wrap gap-4 items-center bg-muted/20">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input 
                  placeholder="Search strategies..." 
                  className="pl-9" 
                  value={search} 
                  onChange={(e) => setSearch(e.target.value)} 
                />
              </div>
              <div className="w-40">
                <Select value={categoryFilter} onValueChange={(val) => val && setCategoryFilter(val)}>
                  <SelectTrigger><SelectValue placeholder="Category" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="w-40">
                <Select value={statusFilter} onValueChange={(val) => val && setStatusFilter(val)}>
                  <SelectTrigger><SelectValue placeholder="Status" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="implemented">Implemented</SelectItem>
                    <SelectItem value="partial">Partial</SelectItem>
                    <SelectItem value="planned">Planned</SelectItem>
                    <SelectItem value="disabled">Disabled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Context Configuration */}
          <div className="flex items-center gap-4 bg-blue-900/10 border border-blue-900/30 p-4 rounded-lg">
            <Settings2 className="w-5 h-5 text-blue-500" />
            <div className="text-sm font-medium">Analysis Context:</div>
            <div className="w-32">
              <Select value={symbol} onValueChange={(val) => val && setSymbol(val)}>
                <SelectTrigger className="h-8"><SelectValue placeholder="Symbol" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="XAUUSD">XAUUSD</SelectItem>
                  <SelectItem value="NQ100">NQ100</SelectItem>
                  <SelectItem value="BTCUSD">BTCUSD</SelectItem>
                  <SelectItem value="EURUSD">EURUSD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="w-24">
              <Select value={timeframe} onValueChange={(val) => val && setTimeframe(val)}>
                <SelectTrigger className="h-8"><SelectValue placeholder="Timeframe" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="M15">M15</SelectItem>
                  <SelectItem value="H1">H1</SelectItem>
                  <SelectItem value="H4">H4</SelectItem>
                  <SelectItem value="D1">D1</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {renderStrategyGrid(filteredStrategies)}
        </TabsContent>

        <TabsContent value="enabled">
          {renderStrategyGrid(strategies.filter(s => s.status === 'implemented' || s.status === 'partial'))}
        </TabsContent>

        <TabsContent value="roadmap">
          {renderRoadmap()}
        </TabsContent>
      </Tabs>

      {/* Strategy Detail Drawer */}
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
          {detailLoading ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">Loading strategy details...</div>
          ) : selectedStrategy ? (
            <div className="space-y-8 pb-10">
              <SheetHeader>
                <div className="flex items-center justify-between">
                   <Badge variant="outline" className="uppercase tracking-widest text-[10px]">{selectedStrategy.category.replace('_', ' ')}</Badge>
                   {getStatusBadge(selectedStrategy.status)}
                </div>
                <SheetTitle className="text-3xl mt-2">{selectedStrategy.name}</SheetTitle>
                <SheetDescription className="text-base text-foreground mt-2">
                  {selectedStrategy.description}
                </SheetDescription>
              </SheetHeader>

              {/* Badges Overview */}
              <div className="flex flex-wrap gap-2 pt-2">
                 <Badge variant="secondary" className="font-normal"><BarChart2 className="w-3 h-3 mr-1"/> Complexity: {selectedStrategy.complexity}</Badge>
                 <Badge variant="secondary" className="font-normal"><AlertTriangle className="w-3 h-3 mr-1"/> Risk: {selectedStrategy.risk_level}</Badge>
              </div>

              {/* How it Works */}
              {selectedStrategy.how_it_works && (
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg flex items-center gap-2"><BookOpen className="w-4 h-4"/> How It Works</h3>
                  <div className="p-4 bg-muted/30 rounded-lg text-sm leading-relaxed">
                    {selectedStrategy.how_it_works}
                  </div>
                </div>
              )}

              {/* Market Conditions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-green-500 flex items-center gap-2"><CheckCircle2 className="w-4 h-4"/> Best Conditions</h3>
                  <ul className="space-y-1">
                    {(selectedStrategy.best_conditions || []).map((c: string, i: number) => (
                      <li key={i} className="text-sm bg-green-500/10 px-2 py-1 rounded border border-green-500/20">{c}</li>
                    ))}
                    {!(selectedStrategy.best_conditions?.length) && <li className="text-sm text-muted-foreground">Not specified</li>}
                  </ul>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-red-500 flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> Weak Conditions</h3>
                  <ul className="space-y-1">
                    {(selectedStrategy.weak_conditions || []).map((c: string, i: number) => (
                      <li key={i} className="text-sm bg-red-500/10 px-2 py-1 rounded border border-red-500/20">{c}</li>
                    ))}
                    {!(selectedStrategy.weak_conditions?.length) && <li className="text-sm text-muted-foreground">Not specified</li>}
                  </ul>
                </div>
              </div>

              {/* Dependencies */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm">Required Indicators</h3>
                  <div className="flex flex-wrap gap-1">
                    {(selectedStrategy.required_indicators || []).map((ind: string, i: number) => (
                      <Badge key={i} variant="outline" className="bg-background">{ind}</Badge>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm">Required Data</h3>
                  <div className="flex flex-wrap gap-1">
                    {(selectedStrategy.required_data || []).map((d: string, i: number) => (
                      <Badge key={i} variant="secondary" className="bg-blue-500/10 text-blue-500">{d}</Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Readiness Checklist */}
              <div className="space-y-2">
                <h3 className="font-semibold text-lg flex items-center gap-2"><Target className="w-4 h-4"/> Module Readiness</h3>
                <div className="grid grid-cols-2 gap-2">
                   {[
                     { label: "Dashboard Analysis", key: "analysis" },
                     { label: "Historical Backtesting", key: "backtesting" },
                     { label: "Forward Testing", key: "forward_testing" },
                     { label: "Live EA Execution", key: "ea_ready" }
                   ].map(item => {
                     const isReady = selectedStrategy.readiness?.[item.key];
                     return (
                       <div key={item.key} className={`flex items-center gap-2 p-2 rounded border ${isReady ? 'border-green-500/30 bg-green-500/5 text-green-500' : 'border-muted bg-muted/30 text-muted-foreground'}`}>
                         {isReady ? <CheckCircle2 className="w-4 h-4"/> : <CircleDashed className="w-4 h-4"/>}
                         <span className="text-sm font-medium">{item.label}</span>
                       </div>
                     )
                   })}
                </div>
              </div>

              {/* Conversion Workflow (If Planned/Partial) */}
              {(selectedStrategy.status === 'planned' || selectedStrategy.status === 'partial') && (
                <div className="space-y-2 border-t pt-6">
                  <h3 className="font-bold text-lg text-primary flex items-center gap-2"><CheckSquare className="w-5 h-5"/> Conversion Workflow</h3>
                  <p className="text-sm text-muted-foreground mb-4">The following steps must be completed to convert this strategy into a fully implemented, executable module.</p>
                  
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold">Implementation Steps</h4>
                      <ul className="space-y-2">
                        {(selectedStrategy.implementation_steps || []).map((step: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm bg-muted/20 p-2 rounded border">
                            <CircleDashed className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    {selectedStrategy.validation_checklist && selectedStrategy.validation_checklist.length > 0 && (
                      <div className="space-y-2 pt-2">
                        <h4 className="text-sm font-semibold text-yellow-500">Validation & QA Checklist</h4>
                        <ul className="space-y-2">
                          {selectedStrategy.validation_checklist.map((step: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm bg-yellow-500/5 p-2 rounded border border-yellow-500/20">
                              <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 shrink-0" />
                              <span>{step}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Limitations */}
              {selectedStrategy.limitations && selectedStrategy.limitations.length > 0 && (
                <div className="space-y-2 pt-6 border-t border-red-500/20">
                  <h3 className="font-semibold text-sm text-red-500 flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> Known Limitations</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {selectedStrategy.limitations.map((lim: string, i: number) => (
                      <li key={i} className="text-sm text-red-400">{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
              
            </div>
          ) : (
            <div className="p-8 text-center text-muted-foreground">Strategy not found.</div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
