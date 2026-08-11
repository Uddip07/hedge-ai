import { apiClient } from '../api/client';

export async function fetchMarketQuote(ticker, refresh = false) {
  const cleanTicker = ticker ? ticker.trim().toUpperCase() : 'RELIANCE.NSE';
  const query = refresh ? '?refresh=true' : '';
  const { data, latencyMs } = await apiClient(`/market/${cleanTicker}${query}`);
  return { data, latencyMs };
}

export async function fetchMarketHistory(ticker) {
  const cleanTicker = ticker ? ticker.trim().toUpperCase() : 'RELIANCE.NSE';
  const { data } = await apiClient(`/market/${cleanTicker}/history`);
  if (!Array.isArray(data)) return [];
  return data.map((d) => {
    const rawDate = d.date || d.timestamp || '';
    const date = typeof rawDate === 'string' ? rawDate.slice(0, 10) : String(rawDate);
    const open = typeof d.open === 'number' ? d.open : parseFloat(d.open ?? d.ohlcv?.open?.money?.amount ?? d.ohlcv?.open ?? 0);
    const high = typeof d.high === 'number' ? d.high : parseFloat(d.high ?? d.ohlcv?.high?.money?.amount ?? d.ohlcv?.high ?? 0);
    const low = typeof d.low === 'number' ? d.low : parseFloat(d.low ?? d.ohlcv?.low?.money?.amount ?? d.ohlcv?.low ?? 0);
    const close = typeof d.close === 'number' ? d.close : parseFloat(d.close ?? d.ohlcv?.close?.money?.amount ?? d.ohlcv?.close ?? 0);
    const volume = typeof d.volume === 'number' ? d.volume : parseFloat(d.volume ?? d.ohlcv?.volume?.value ?? d.ohlcv?.volume ?? 0);
    return {
      date,
      timestamp: d.timestamp || d.date,
      open,
      high,
      low,
      close,
      volume,
    };
  });
}

export async function fetchDailyMarketSummary() {
  try {
    const { data } = await apiClient('/market/summary/daily');
    return data;
  } catch {
    return null;
  }
}

export async function fetchMarketDataStats() {
  try {
    const { data } = await apiClient('/api/v1/market-data/stats');
    return data;
  } catch {
    return null;
  }
}

export async function fetchSymbolsList() {
  try {
    const { data } = await apiClient('/api/v1/market-data/symbols');
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

export async function fetchCompanyBySymbol(symbol) {
  const cleanSym = symbol ? symbol.trim().toUpperCase() : 'RELIANCE';
  const { data } = await apiClient(`/api/v1/market-data/companies/${cleanSym}`);
  return data;
}

export async function fetchHistoricalPrices(symbol, startDate, endDate, limit = 500) {
  const cleanSym = symbol ? symbol.trim().toUpperCase() : 'RELIANCE';
  let query = `?limit=${limit}`;
  if (startDate) query += `&start_date=${startDate}`;
  if (endDate) query += `&end_date=${endDate}`;
  const { data } = await apiClient(`/api/v1/market-data/prices/${cleanSym}${query}`);
  return Array.isArray(data) ? data : [];
}

export async function fetchTickerNews(ticker) {
  const cleanTicker = ticker ? ticker.trim().toUpperCase() : 'RELIANCE.NSE';
  try {
    const { data } = await apiClient(`/market/${cleanTicker}/news`);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

export async function ingestNews(tickers = null) {
  const payload = tickers ? { tickers } : {};
  const { data } = await apiClient('/market/news/ingest', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}

export async function syncMarketData(symbols, days = 30) {
  const { data } = await apiClient('/api/v1/market-data/sync', {
    method: 'POST',
    body: JSON.stringify({ symbols, days }),
  });
  return data;
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
    'ICICIBANK.NSE',
    'SBIN.NSE',
  ];
  const results = await Promise.allSettled(tickers.map((t) => fetchMarketQuote(t)));

  const quotes = {};
  results.forEach((res, i) => {
    if (res.status === 'fulfilled') {
      quotes[tickers[i]] = res.value.data;
    }
  });

  return quotes;
}
