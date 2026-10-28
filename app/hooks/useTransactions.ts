import { useMutation, useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { Child, Transaction, TransactionInput } from '@digital-bank/shared';
import { getJsonAuth, postJsonAuth } from '@/lib/apiClient';

export function useChildrenQuery() {
  return useQuery({
    queryKey: ['children'],
    queryFn: () => getJsonAuth<{ children: Child[] }>('/children'),
  });
}

export function useFamilyTransactionsQuery(childId?: string) {
  return useQuery({
    queryKey: ['familyTransactions', childId ?? 'all'],
    queryFn: () =>
      getJsonAuth<{ balances: Record<string, number>; transactions: Transaction[] }>(
        childId ? `/transactions?childId=${childId}` : '/transactions'
      ),
    placeholderData: keepPreviousData,
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
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['familyTransactions'] }),
  });
}
