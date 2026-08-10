import { apiClient } from '../api/client';
import { MarketQuote } from '../types/api';

export interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export async function fetchMarketQuote(
  ticker: string
): Promise<{ data: MarketQuote; latencyMs: number }> {
  const { data, latencyMs } = await apiClient<MarketQuote>(`/market/${ticker}`);
  return { data, latencyMs };
}

export async function fetchMarketHistory(ticker: string): Promise<ChartDataPoint[]> {
  const { data } = await apiClient<ChartDataPoint[]>(`/market/${ticker}/history`);
  return Array.isArray(data) ? data : [];
}

export async function fetchMarketOverview() {
  const tickers = [
    'NIFTY.NSE',
    'BANKNIFTY.NSE',
    'SENSEX.BSE',
    'RELIANCE.NSE',
    'TCS.NSE',
    'INFY.NSE',
    'HDFCBANK.NSE',
  ];
  const results = await Promise.allSettled(tickers.map((t) => fetchMarketQuote(t)));

  const quotes: Record<string, MarketQuote> = {};
  results.forEach((res, i) => {
    if (res.status === 'fulfilled') {
      quotes[tickers[i]] = res.value.data;
    }
  });

  return quotes;
}
