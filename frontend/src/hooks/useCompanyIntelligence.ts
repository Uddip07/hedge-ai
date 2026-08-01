import { useQuery } from '@tanstack/react-query';
import { fetchCompanyIntelligence } from '../services/companyService';

export function useCompanyIntelligence(ticker: string, enabled = false) {
  return useQuery({
    queryKey: ['companyIntelligence', ticker],
    queryFn: () => fetchCompanyIntelligence(ticker),
    enabled: enabled && Boolean(ticker),
    staleTime: 5 * 60 * 1000,
  });
}
