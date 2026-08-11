import { apiClient } from '../api/client';

export async function fetchCompanyIntelligence(ticker) {
  const cleanTicker = ticker ? ticker.trim().toUpperCase() : 'RELIANCE.NSE';
  const { data } = await apiClient(`/company-intelligence/${cleanTicker}`);
  return data;
}

export async function postAnalyzeStock(payload) {
  const { data } = await apiClient('/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}
