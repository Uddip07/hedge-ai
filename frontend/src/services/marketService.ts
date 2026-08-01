import { apiClient } from '../api/client';
import { MarketQuote } from '../types/api';

export async function fetchMarketQuote(ticker: string): Promise<{ data: MarketQuote; latencyMs: number }> {
  const { data, latencyMs } = await apiClient<MarketQuote>(`/market/${ticker}`);
  return { data, latencyMs };
}

export async function fetchMarketOverview() {
  const tickers = ['NIFTY.NSE', 'BANKNIFTY.NSE', 'SENSEX.BSE', 'RELIANCE.NSE', 'TCS.NSE', 'INFY.NSE', 'HDFCBANK.NSE'];
  const results = await Promise.allSettled(tickers.map((t) => fetchMarketQuote(t)));

  const quotes: Record<string, MarketQuote> = {};
  results.forEach((res, i) => {
    if (res.status === 'fulfilled') {
      quotes[tickers[i]] = res.value.data;
    }
  });

  return quotes;
}
