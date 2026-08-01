import { apiClient } from '../api/client';
import { EvaluateCommitteeRequest, EvaluateCommitteeResponse } from '../types/api';

export async function evaluateCommittee(payload: EvaluateCommitteeRequest): Promise<EvaluateCommitteeResponse> {
  const { data } = await apiClient<EvaluateCommitteeResponse>('/committee/evaluate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}
