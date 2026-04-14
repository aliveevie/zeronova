import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowDownToLine, ArrowUpFromLine } from 'lucide-react'
import { useVaultStats } from '@/hooks/useVaultStats'
import { useNavHistory } from '@/hooks/useNavHistory'
import { useSignal } from '@/hooks/useSignal'
import { useUserPosition } from '@/hooks/useUserPosition'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import VaultCard from '@/components/VaultCard'
import NavChart from '@/components/NavChart'
import SentimentBadge from '@/components/SentimentBadge'
import PositionTable from '@/components/PositionTable'

export default function Dashboard() {
  const [navWindow, setNavWindow] = useState<'7d' | '30d' | 'all'>('7d')

  const { data: stats, isLoading: statsLoading } = useVaultStats()
  const { data: navHistory, isLoading: navLoading } = useNavHistory(navWindow)
  const { data: signal, isLoading: signalLoading } = useSignal('BTC')
  const { data: userPosition } = useUserPosition()

  const { data: positions, isLoading: positionsLoading } = useQuery({
    queryKey: ['vault', 'positions'],
    queryFn: api.vault.getPositions,
    refetchInterval: 30_000,
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-zerova-muted mt-1">
            Delta-neutral yield powered by Pacifica perpetuals
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/deposit" className="btn-primary flex items-center gap-2">
            <ArrowDownToLine size={16} />
            Deposit
          </Link>
          <Link to="/withdraw" className="btn-secondary flex items-center gap-2">
            <ArrowUpFromLine size={16} />
            Withdraw
          </Link>
        </div>
      </div>

      {userPosition && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-zerova-teal/10 to-emerald-500/10 border-zerova-teal/20"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-zerova-muted">Your Position</p>
              <p className="text-2xl font-semibold font-mono mt-1">
                {parseFloat(userPosition.zv_usdc_balance).toFixed(4)} zvUSDC
              </p>
              <p className="text-sm text-zerova-muted mt-1">
                ≈ ${parseFloat(userPosition.usdc_current_value).toFixed(2)} USDC
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-zerova-muted">Unrealised Yield</p>
              <p className={`text-2xl font-semibold font-mono mt-1 ${
                parseFloat(userPosition.unrealised_yield) >= 0 ? 'text-zerova-success' : 'text-zerova-danger'
              }`}>
                {parseFloat(userPosition.unrealised_yield) >= 0 ? '+' : ''}
                ${parseFloat(userPosition.unrealised_yield).toFixed(2)}
              </p>
              <p className="text-sm text-zerova-muted mt-1">
                {userPosition.yield_pct >= 0 ? '+' : ''}{userPosition.yield_pct.toFixed(2)}%
              </p>
            </div>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <VaultCard stats={stats ?? null} isLoading={statsLoading} />
        </div>
        <div>
          <SentimentBadge signal={signal ?? null} isLoading={signalLoading} />
        </div>
      </div>

      <NavChart
        data={navHistory?.data ?? []}
        isLoading={navLoading}
        window={navWindow}
        onWindowChange={setNavWindow}
      />

      <PositionTable
        positions={positions?.positions ?? []}
        isLoading={positionsLoading}
      />
    </div>
  )
}
