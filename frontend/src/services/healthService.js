import { apiClient } from '../api/client';

export async function fetchHealth() {
  const { data, latencyMs } = await apiClient('/health');
  return { data, latencyMs };
}

export async function fetchDetailedHealth() {
  try {
    const { data, latencyMs } = await apiClient('/health/detailed');
    return { data, latencyMs };
  } catch {
    return {
      data: {
        status: 'unhealthy',
        components: {
          database: { status: 'unhealthy', error: 'Connection failed' },
          redis: { status: 'disabled' },
          yahoo_provider: { status: 'degraded' },
          data_freshness: { status: 'empty' },
        },
      },
      latencyMs: 0,
    };
  }
}

export async function fetchRoot() {
  const { data, latencyMs } = await apiClient('/');
  return { data, latencyMs };
}

export async function fetchVersion() {
  const { data, latencyMs } = await apiClient('/version');
  return { data, latencyMs };
}
