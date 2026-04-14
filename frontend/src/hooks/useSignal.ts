import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useVaultStore } from '@/store/vault'
import { useEffect } from 'react'

export function useSignal(asset: string = 'BTC') {
  const setSignal = useVaultStore((s) => s.setSignal)

  const query = useQuery({
    queryKey: ['signal', asset],
    queryFn: () => api.signal.get(asset),
    refetchInterval: 60_000,
  })

  useEffect(() => {
    if (query.data) {
      setSignal(query.data)
    }
  }, [query.data, setSignal])

  return query
}
