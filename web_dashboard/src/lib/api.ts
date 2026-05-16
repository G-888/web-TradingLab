const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';
const API_KEY = process.env.NEXT_PUBLIC_DASHBOARD_API_KEY || '';

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${API_KEY}`);
  }
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
    cache: 'no-store' // We want fresh data for the dashboard
  });

  if (!response.ok) {
    console.error(`API Error: ${response.status} ${response.statusText} for ${url}`);
    // If backend returns 401 or offline, return empty/safe instead of crashing
    if (response.status === 401 || response.status === 403 || response.status >= 500) {
      return null;
    }
  }

  try {
    return await response.json();
  } catch (err) {
    console.error('Failed to parse JSON', err);
    return null;
  }
}

export const api = {
  getHealth: async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
      return await res.json();
    } catch {
      return { status: 'error', service: 'offline' };
    }
  },
  getOverview: () => fetchWithAuth('/api/overview'),
  getLatestSignals: () => fetchWithAuth('/api/signals/latest'),
  getSignalHistory: (symbol = 'XAUUSD', timeframe = '') => {
    let url = `/api/signals/history?symbol=${symbol}`;
    if (timeframe) url += `&timeframe=${timeframe}`;
    return fetchWithAuth(url);
  },
  getBacktestRuns: () => fetchWithAuth('/api/backtests/runs'),
  getBacktestTrades: (runId: number) => fetchWithAuth(`/api/backtests/${runId}/trades`),
  getAlerts: () => fetchWithAuth('/api/alerts'),
  getPerformanceSnapshots: () => fetchWithAuth('/api/performance/snapshots'),
  getMarketAnalysis: (data: { symbol: string; timeframe: string }) => fetchWithAuth('/api/analysis/market', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getStrategies: () => fetchWithAuth('/api/strategies'),
  getEnabledStrategies: () => fetchWithAuth('/api/strategies/enabled'),
  getStrategyCategories: () => fetchWithAuth('/api/strategies/categories'),
  getStrategyRoadmap: () => fetchWithAuth('/api/strategies/roadmap'),
  getStrategy: (id: string) => fetchWithAuth(`/api/strategies/${id}`),
  getStrategyDetail: (id: string) => fetchWithAuth(`/api/strategies/${id}/detail`),
  analyzeStrategy: (data: { strategy_id: string; symbol: string; timeframe: string }) => fetchWithAuth('/api/strategies/analyze', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getStrategiesSummary: (symbol: string, timeframe: string) => fetchWithAuth(`/api/strategies/summary?symbol=${symbol}&timeframe=${timeframe}`),
  runBacktest: (data: any) => fetchWithAuth('/api/backtests/run', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getForwardTestSessions: () => fetchWithAuth('/api/forward-tests/sessions'),
  startForwardTest: (data: { symbol: string; strategy: string; timeframe: string }) => fetchWithAuth('/api/forward-tests/start', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  stopForwardTest: (sessionId: number) => fetchWithAuth(`/api/forward-tests/stop?session_id=${sessionId}`, {
    method: 'POST',
  }),
  getForwardTestTrades: (sessionId: number) => fetchWithAuth(`/api/forward-tests/${sessionId}/trades`),
  getMarketOutlook: (symbol: string) => fetchWithAuth(`/api/outlook/market?symbol=${symbol}`),
  getNewsOutlook: (symbol: string) => fetchWithAuth(`/api/outlook/news?symbol=${symbol}`),
  getPerformanceSummary: () => fetchWithAuth('/api/performance/summary'),
  getPerformanceByStrategy: () => fetchWithAuth('/api/performance/by-strategy'),
  getCandles: (symbol: string, timeframe: string, limit: number = 300) => 
    fetchWithAuth(`/api/market/candles?symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`),
  getStrategyLabTestable: (type: string) => fetchWithAuth(`/api/strategy-lab/testable?type=${type}`),
  runStrategyLabBacktestAll: (data: any) => fetchWithAuth('/api/strategy-lab/backtest-all', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  startStrategyLabForwardTest: (data: any) => fetchWithAuth('/api/strategy-lab/forward-test/start', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getStrategyLabRuns: () => fetchWithAuth('/api/strategy-lab/runs'),
  getStrategyLabRunDetails: (runId: number) => fetchWithAuth(`/api/strategy-lab/runs/${runId}`),
  getStrategyLabRankings: (symbol: string, timeframe: string) => fetchWithAuth(`/api/strategy-lab/rankings?symbol=${symbol}&timeframe=${timeframe}`),
  getStrategyLabCompare: (symbol: string, timeframe: string) => fetchWithAuth(`/api/strategy-lab/compare?symbol=${symbol}&timeframe=${timeframe}`),
};
