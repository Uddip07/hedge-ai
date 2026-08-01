import { useMutation } from '@tanstack/react-query';
import { evaluateCommittee } from '../services/committeeService';
import { EvaluateCommitteeRequest } from '../types/api';

export function useEvaluateCommittee() {
  return useMutation({
    mutationFn: (payload: EvaluateCommitteeRequest) => evaluateCommittee(payload),
  });
}
