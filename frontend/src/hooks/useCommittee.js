import { useMutation } from '@tanstack/react-query';
import { evaluateCommittee } from '../services/committeeService';

export function useEvaluateCommittee() {
  return useMutation({
    mutationFn: (payload) => evaluateCommittee(payload),
  });
}
