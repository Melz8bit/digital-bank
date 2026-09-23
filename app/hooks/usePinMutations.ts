import { useMutation, useQuery } from '@tanstack/react-query';
import type { PinInput } from '@digital-bank/shared';
import { getJsonAuth, postJsonAuth } from '@/lib/apiClient';

export function usePinStatusQuery() {
  return useQuery({
    queryKey: ['pinStatus'],
    queryFn: () => getJsonAuth<{ pinSet: boolean }>('/pin/status'),
  });
}

export function useSetPinMutation() {
  return useMutation({
    mutationFn: (input: PinInput) => postJsonAuth<{ message: string }>('/pin/set', input),
  });
}

export function useVerifyPinMutation() {
  return useMutation({
    mutationFn: (input: PinInput) => postJsonAuth<{ message: string }>('/pin/verify', input),
  });
}
