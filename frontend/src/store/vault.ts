import { create } from 'zustand'
import type { VaultStats, UserPosition, SignalScore } from '@/types'

interface VaultStore {
  stats: VaultStats | null
  userPosition: UserPosition | null
  signal: SignalScore | null
  isLoading: boolean
  error: string | null

  setStats: (stats: VaultStats) => void
  setUserPosition: (position: UserPosition | null) => void
  setSignal: (signal: SignalScore) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const initialState = {
  stats: null,
  userPosition: null,
  signal: null,
  isLoading: false,
  error: null,
}

export const useVaultStore = create<VaultStore>((set) => ({
  ...initialState,

  setStats: (stats) => set({ stats }),
  setUserPosition: (userPosition) => set({ userPosition }),
  setSignal: (signal) => set({ signal }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}))
