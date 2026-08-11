import { useQuery } from '@tanstack/react-query';
import {
  fetchMarketOverview,
  fetchMarketQuote,
  fetchMarketHistory,
  fetchDailyMarketSummary,
  fetchMarketDataStats,
  fetchSymbolsList,
} from '../services/marketService';
import { useSettingsStore } from '../store/useSettingsStore';

export function useMarketQuote(ticker, enabled = true) {
  const { autoRefreshInterval } = useSettingsStore();

  return useQuery({
    queryKey: ['marketQuote', ticker],
    queryFn: () => fetchMarketQuote(ticker),
    enabled: enabled && Boolean(ticker),
    refetchInterval: autoRefreshInterval > 0 ? autoRefreshInterval : false,
  });
}

export function useMarketHistory(ticker, enabled = true) {
  return useQuery({
    queryKey: ['marketHistory', ticker],
    queryFn: () => fetchMarketHistory(ticker),
    enabled: enabled && Boolean(ticker),
  });
}

export function useDailyMarketSummary() {
  const { autoRefreshInterval } = useSettingsStore();

  return useQuery({
    queryKey: ['dailyMarketSummary'],
    queryFn: fetchDailyMarketSummary,
    refetchInterval: autoRefreshInterval > 0 ? autoRefreshInterval * 2 : false,
  });
}

export function useMarketDataStats() {
  return useQuery({
    queryKey: ['marketDataStats'],
    queryFn: fetchMarketDataStats,
  });
}

export function useSymbolsList() {
  return useQuery({
    queryKey: ['symbolsList'],
    queryFn: fetchSymbolsList,
  });
}

export function useMarketOverview() {
  const { autoRefreshInterval } = useSettingsStore();

  return useQuery({
    queryKey: ['marketOverview'],
    queryFn: fetchMarketOverview,
    refetchInterval: autoRefreshInterval > 0 ? autoRefreshInterval : false,
  });
}
