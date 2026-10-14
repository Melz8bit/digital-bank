import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Child, Transaction, TransactionInput } from '@digital-bank/shared';
import { getJsonAuth, postJsonAuth } from '@/lib/apiClient';

export function useChildrenQuery() {
  return useQuery({
    queryKey: ['children'],
    queryFn: () => getJsonAuth<{ children: Child[] }>('/children'),
  });
}

export function useTransactionsQuery(childId: string | undefined) {
  return useQuery({
    queryKey: ['transactions', childId],
    queryFn: () =>
      getJsonAuth<{ balance: number; transactions: Transaction[] }>(
        `/children/${childId}/transactions`
      ),
    enabled: !!childId,
  });
}

export function useCreateTransactionMutation(childId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: TransactionInput) =>
      postJsonAuth<{ transaction: Transaction; balance: number }>(
        `/children/${childId}/transactions`,
        input
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions', childId] }),
  });
}
