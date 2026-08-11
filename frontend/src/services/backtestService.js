import { apiClient } from '../api/client';

export async function executeBacktest(payload) {
  const { data } = await apiClient('/api/v1/backtest/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}

export async function fetchBacktestRun(runId) {
  const { data } = await apiClient(`/api/v1/backtest/${runId}`);
  return data;
}
