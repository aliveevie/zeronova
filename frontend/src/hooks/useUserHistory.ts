import { useQuery } from '@tanstack/react-query'
import { usePrivy } from '@privy-io/react-auth'
import { api } from '@/lib/api'

export function useUserHistory() {
  const { user, authenticated } = usePrivy()
  const wallet = user?.wallet?.address

  return useQuery({
    queryKey: ['user', 'history', wallet],
    queryFn: () => api.user.getHistory(wallet!),
    enabled: authenticated && !!wallet,
  })
}
