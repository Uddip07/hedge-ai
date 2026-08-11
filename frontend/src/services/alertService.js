import { apiClient } from '../api/client';

export async function fetchRecentAlerts(limit = 20) {
  try {
    const { data } = await apiClient(`/api/v1/alerts/recent?limit=${limit}`);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

export async function dispatchAlert(payload) {
  const { data } = await apiClient('/api/v1/alerts/dispatch', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}
