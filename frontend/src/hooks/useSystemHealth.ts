import { useQuery } from '@tanstack/react-query';
import { fetchHealth, fetchRoot, fetchVersion } from '../services/healthService';
import { useSettingsStore } from '../store/useSettingsStore';

export function useSystemHealth() {
  const { autoRefreshInterval } = useSettingsStore();

  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: autoRefreshInterval,
  });

  const rootQuery = useQuery({
    queryKey: ['root'],
    queryFn: fetchRoot,
    refetchInterval: autoRefreshInterval,
  });

  const versionQuery = useQuery({
    queryKey: ['version'],
    queryFn: fetchVersion,
    refetchInterval: autoRefreshInterval,
  });

  return {
    health: healthQuery,
    root: rootQuery,
    version: versionQuery,
  };
}
