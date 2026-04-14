import { motion } from 'framer-motion'
import { TrendingUp, Shield, Activity } from 'lucide-react'
import type { VaultStats } from '@/types'

interface VaultCardProps {
  stats: VaultStats | null
  isLoading: boolean
}

export default function VaultCard({ stats, isLoading }: VaultCardProps) {
  if (isLoading || !stats) {
    return (
      <div className="card glow animate-pulse">
        <div className="h-6 w-32 bg-zerova-border rounded mb-4" />
        <div className="h-10 w-24 bg-zerova-border rounded mb-2" />
        <div className="h-4 w-40 bg-zerova-border rounded" />
      </div>
    )
  }

  const tvlFormatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(parseFloat(stats.tvl_usdc))

  const statusColors = {
    active: 'text-zerova-success',
    transitioning: 'text-zerova-warning',
    parked: 'text-zerova-muted',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card glow"
    >
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <span className="text-gradient">zvUSDC Vault</span>
            <span className="text-sm text-zerova-muted font-normal">({stats.asset})</span>
          </h3>
          <p className="text-sm text-zerova-muted mt-1">Delta-neutral yield strategy</p>
        </div>
        <div className={`flex items-center gap-1.5 text-sm ${statusColors[stats.status]}`}>
          <Activity size={14} />
          <span className="capitalize">{stats.status}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <p className="stat-label">Total Value Locked</p>
          <p className="stat-value text-white">{tvlFormatted}</p>
        </div>
        <div>
          <p className="stat-label">APY (7d)</p>
          <p className="stat-value text-zerova-teal flex items-center gap-1">
            <TrendingUp size={20} />
            {stats.apy_7d}%
          </p>
        </div>
        <div>
          <p className="stat-label">NAV / Share</p>
          <p className="stat-value text-white">${parseFloat(stats.nav_per_share).toFixed(4)}</p>
        </div>
        <div>
          <p className="stat-label">Net Delta</p>
          <p className="stat-value text-white flex items-center gap-1">
            <Shield size={18} className="text-zerova-success" />
            {parseFloat(stats.net_delta).toFixed(4)}
          </p>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-zerova-border">
        <div className="flex items-center justify-between text-sm">
          <span className="text-zerova-muted">Funding Rate (8h)</span>
          <span className={stats.current_funding_rate >= 0 ? 'text-zerova-success' : 'text-zerova-danger'}>
            {(stats.current_funding_rate * 100).toFixed(4)}%
          </span>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="text-zerova-muted">Margin Ratio</span>
          <span className={stats.margin_ratio > 0.3 ? 'text-zerova-success' : 'text-zerova-warning'}>
            {(stats.margin_ratio * 100).toFixed(1)}%
          </span>
        </div>
      </div>
    </motion.div>
  )
}
