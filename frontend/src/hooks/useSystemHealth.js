import { useQuery } from '@tanstack/react-query';
import {
  fetchHealth,
  fetchDetailedHealth,
  fetchRoot,
  fetchVersion,
} from '../services/healthService';
import { useSettingsStore } from '../store/useSettingsStore';

export function useSystemHealth() {
  const { autoRefreshInterval } = useSettingsStore();

  const health = useQuery({
    queryKey: ['systemHealth'],
    queryFn: fetchHealth,
    refetchInterval: autoRefreshInterval > 0 ? autoRefreshInterval : false,
  });

  const detailedHealth = useQuery({
    queryKey: ['systemDetailedHealth'],
    queryFn: fetchDetailedHealth,
    refetchInterval: autoRefreshInterval > 0 ? autoRefreshInterval * 2 : false,
  });

  const version = useQuery({
    queryKey: ['systemVersion'],
    queryFn: fetchVersion,
    staleTime: 60000,
  });

  const root = useQuery({
    queryKey: ['systemRoot'],
    queryFn: fetchRoot,
    staleTime: 60000,
  });

  return {
    health,
    detailedHealth,
    version,
    root,
  };
}
