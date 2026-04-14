import { useQuery } from '@tanstack/react-query'
import { usePrivy } from '@privy-io/react-auth'
import { api } from '@/lib/api'
import { useVaultStore } from '@/store/vault'
import { useEffect } from 'react'

export function useUserPosition() {
  const { user, authenticated } = usePrivy()
  const setUserPosition = useVaultStore((s) => s.setUserPosition)
  const wallet = user?.wallet?.address

  const query = useQuery({
    queryKey: ['user', 'position', wallet],
    queryFn: () => api.user.getPosition(wallet!),
    enabled: authenticated && !!wallet,
    refetchInterval: 30_000,
  })

  useEffect(() => {
    if (query.data) {
      setUserPosition(query.data)
    } else if (!authenticated) {
      setUserPosition(null)
    }
  }, [query.data, authenticated, setUserPosition])

  return query
}
