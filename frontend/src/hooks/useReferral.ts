import { useQuery } from '@tanstack/react-query'
import { usePrivy } from '@privy-io/react-auth'
import { api } from '@/lib/api'

export function useReferral() {
  const { user, authenticated } = usePrivy()
  const wallet = user?.wallet?.address

  return useQuery({
    queryKey: ['user', 'referral', wallet],
    queryFn: () => api.user.getReferral(wallet!),
    enabled: authenticated && !!wallet,
  })
}
