import { useQuery } from '@tanstack/react-query';
import { Family } from '@digital-bank/shared';
import { getJsonAuth } from '@/lib/apiClient';

export function useFamilyQuery() {
  return useQuery({
    queryKey: ['family'],
    queryFn: () => getJsonAuth<{ family: Family }>('/family'),
  });
}
