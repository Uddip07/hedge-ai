import { apiClient } from '../api/client';
import { AnalyzeStockRequest, AnalyzeStockResponse, CompanyIntelligenceResponse } from '../types/api';

export async function fetchCompanyIntelligence(ticker: string): Promise<CompanyIntelligenceResponse> {
  const { data } = await apiClient<CompanyIntelligenceResponse>(`/company-intelligence/${ticker}`);
  return data;
}

export async function postAnalyzeStock(payload: AnalyzeStockRequest): Promise<AnalyzeStockResponse> {
  const { data } = await apiClient<AnalyzeStockResponse>('/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}
