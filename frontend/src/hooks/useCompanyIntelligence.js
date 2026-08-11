import { useQuery } from '@tanstack/react-query';
import { fetchCompanyIntelligence } from '../services/companyService';

export function useCompanyIntelligence(ticker, enabled = true) {
  return useQuery({
    queryKey: ['companyIntelligence', ticker],
    queryFn: () => fetchCompanyIntelligence(ticker),
    enabled: enabled && Boolean(ticker),
  });
}
