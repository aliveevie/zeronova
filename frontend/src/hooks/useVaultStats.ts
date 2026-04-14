import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useVaultStore } from '@/store/vault'
import { useEffect } from 'react'

export function useVaultStats() {
  const setStats = useVaultStore((s) => s.setStats)

  const query = useQuery({
    queryKey: ['vault', 'stats'],
    queryFn: api.vault.getStats,
    refetchInterval: 30_000,
  })

  useEffect(() => {
    if (query.data) {
      setStats(query.data)
    }
  }, [query.data, setStats])

  return query
}
