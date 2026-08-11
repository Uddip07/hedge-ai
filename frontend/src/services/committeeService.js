import { apiClient } from '../api/client';

export async function evaluateCommittee(payload) {
  const cleanTicker = payload.ticker ? payload.ticker.trim().toUpperCase() : 'RELIANCE.NSE';
  const body = {
    ticker: cleanTicker,
    horizon: payload.horizon || 'LONG_TERM',
    style: payload.style || 'BALANCED',
    user_query: payload.user_query || 'Execute comprehensive institutional investment analysis.',
  };

  const { data } = await apiClient('/committee/evaluate', {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return data;
}
