import type {
  VaultStats,
  NavHistoryResponse,
  PositionsResponse,
  UserPosition,
  UserHistoryEvent,
  ReferralInfo,
  SignalScore,
  DepositResponse,
  WithdrawResponse,
} from '@/types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${res.status}`)
  }

  return res.json()
}

export const api = {
  vault: {
    getStats: () => fetchJSON<VaultStats>('/api/v1/vault/stats'),

    getNavHistory: (window: '7d' | '30d' | 'all' = '7d') =>
      fetchJSON<NavHistoryResponse>(`/api/v1/vault/nav/history?window=${window}`),

    getPositions: () => fetchJSON<PositionsResponse>('/api/v1/vault/positions'),

    deposit: (wallet: string, amount_usdc: number, referral_code?: string, source_chain?: string) =>
      fetchJSON<DepositResponse>('/api/v1/vault/deposit', {
        method: 'POST',
        body: JSON.stringify({ wallet, amount_usdc, referral_code, source_chain }),
      }),

    withdraw: (wallet: string, zv_usdc_amount: number) =>
      fetchJSON<WithdrawResponse>('/api/v1/vault/withdraw', {
        method: 'POST',
        body: JSON.stringify({ wallet, zv_usdc_amount }),
      }),
  },

  user: {
    getPosition: (wallet: string) =>
      fetchJSON<UserPosition>(`/api/v1/user/${wallet}/position`),

    getHistory: (wallet: string) =>
      fetchJSON<UserHistoryEvent[]>(`/api/v1/user/${wallet}/history`),

    getReferral: (wallet: string) =>
      fetchJSON<ReferralInfo>(`/api/v1/user/${wallet}/referral`),
  },

  signal: {
    get: (asset: string) => fetchJSON<SignalScore>(`/api/v1/signal/${asset}`),
  },
}
