import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useNavHistory(window: '7d' | '30d' | 'all' = '7d') {
  return useQuery({
    queryKey: ['vault', 'nav-history', window],
    queryFn: () => api.vault.getNavHistory(window),
    refetchInterval: 60_000,
  })
}
