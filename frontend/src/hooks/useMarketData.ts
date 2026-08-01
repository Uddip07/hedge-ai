import { useQuery } from '@tanstack/react-query';
import { fetchMarketOverview, fetchMarketQuote } from '../services/marketService';
import { useSettingsStore } from '../store/useSettingsStore';

export function useMarketQuote(ticker: string, enabled = true) {
  const { autoRefreshInterval } = useSettingsStore();

  return useQuery({
    queryKey: ['marketQuote', ticker],
    queryFn: () => fetchMarketQuote(ticker),
    enabled: enabled && Boolean(ticker),
    refetchInterval: autoRefreshInterval,
  });
}

export function useMarketOverview() {
  const { autoRefreshInterval } = useSettingsStore();

  return useQuery({
    queryKey: ['marketOverview'],
    queryFn: fetchMarketOverview,
    refetchInterval: autoRefreshInterval,
  });
}
