import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp, DollarSign, Percent, Activity } from 'lucide-react'
import { useVaultStats } from '@/hooks/useVaultStats'
import { useNavHistory } from '@/hooks/useNavHistory'
import { api } from '@/lib/api'

export default function Analytics() {
  const [window, setWindow] = useState<'7d' | '30d' | 'all'>('30d')
  const { data: stats } = useVaultStats()
  const { data: navHistory, isLoading: navLoading } = useNavHistory(window)

  useQuery({
    queryKey: ['vault', 'positions'],
    queryFn: api.vault.getPositions,
  })

  const chartData = navHistory?.data.map((point) => ({
    date: new Date(point.timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    nav: parseFloat(point.nav_per_share),
    tvl: parseFloat(point.total_assets) / 1_000_000,
  })) ?? []

  const totalFundingReceived = stats 
    ? parseFloat(stats.total_funding_received) 
    : 0
  const totalFundingPaid = stats 
    ? parseFloat(stats.total_funding_paid) 
    : 0
  const netFunding = totalFundingReceived - totalFundingPaid

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Protocol Analytics</h1>
        <p className="text-zerova-muted mt-1">
          Comprehensive view of Zerova protocol performance
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Value Locked',
            value: stats ? `$${(parseFloat(stats.tvl_usdc) / 1_000_000).toFixed(2)}M` : '—',
            icon: DollarSign,
            color: 'text-zerova-teal',
          },
          {
            label: 'APY (7d)',
            value: stats ? `${stats.apy_7d}%` : '—',
            icon: TrendingUp,
            color: 'text-zerova-success',
          },
          {
            label: 'Net Funding Earned',
            value: `$${netFunding.toFixed(2)}`,
            icon: Percent,
            color: netFunding >= 0 ? 'text-zerova-success' : 'text-zerova-danger',
          },
          {
            label: 'Vault Status',
            value: stats?.status ? stats.status.charAt(0).toUpperCase() + stats.status.slice(1) : '—',
            icon: Activity,
            color: stats?.status === 'active' ? 'text-zerova-success' : 'text-zerova-warning',
          },
        ].map((stat, idx) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="card"
          >
            <div className={`w-8 h-8 rounded-lg bg-zerova-dark flex items-center justify-center mb-3 ${stat.color}`}>
              <stat.icon size={18} />
            </div>
            <p className="stat-label">{stat.label}</p>
            <p className={`stat-value ${stat.color}`}>{stat.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">TVL Over Time</h3>
            <div className="flex items-center gap-1 bg-zerova-dark rounded-lg p-1">
              {(['7d', '30d', 'all'] as const).map((w) => (
                <button
                  key={w}
                  onClick={() => setWindow(w)}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    window === w
                      ? 'bg-zerova-card text-zerova-teal'
                      : 'text-zerova-muted hover:text-white'
                  }`}
                >
                  {w === 'all' ? 'All' : w.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {navLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-zerova-teal border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="tvlGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00E5CC" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#00E5CC" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#6B7280', fontSize: 12 }}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#6B7280', fontSize: 12 }}
                    tickFormatter={(v) => `$${v.toFixed(1)}M`}
                    width={60}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#111827',
                      border: '1px solid #1F2937',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => [`$${value.toFixed(2)}M`, 'TVL']}
                  />
                  <Area
                    type="monotone"
                    dataKey="tvl"
                    stroke="#00E5CC"
                    strokeWidth={2}
                    fill="url(#tvlGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-6">Yield Attribution</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zerova-muted">Funding Received</span>
                <span className="text-sm font-mono text-zerova-success">
                  +${totalFundingReceived.toFixed(2)}
                </span>
              </div>
              <div className="h-2 bg-zerova-dark rounded-full overflow-hidden">
                <div
                  className="h-full bg-zerova-success rounded-full"
                  style={{ width: `${Math.min(100, (totalFundingReceived / (totalFundingReceived + totalFundingPaid + 1)) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zerova-muted">Funding Paid</span>
                <span className="text-sm font-mono text-zerova-danger">
                  -${totalFundingPaid.toFixed(2)}
                </span>
              </div>
              <div className="h-2 bg-zerova-dark rounded-full overflow-hidden">
                <div
                  className="h-full bg-zerova-danger rounded-full"
                  style={{ width: `${Math.min(100, (totalFundingPaid / (totalFundingReceived + totalFundingPaid + 1)) * 100)}%` }}
                />
              </div>
            </div>

            <div className="pt-4 border-t border-zerova-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zerova-muted">Protocol Fees</span>
                <span className="text-sm font-mono">
                  ${stats ? parseFloat(stats.protocol_fees).toFixed(2) : '0.00'}
                </span>
              </div>
            </div>

            <div className="pt-4 border-t border-zerova-border">
              <div className="flex items-center justify-between">
                <span className="font-medium">Net Yield to Depositors</span>
                <span className={`font-mono font-semibold ${
                  netFunding - (stats ? parseFloat(stats.protocol_fees) : 0) >= 0
                    ? 'text-zerova-success'
                    : 'text-zerova-danger'
                }`}>
                  ${(netFunding - (stats ? parseFloat(stats.protocol_fees) : 0)).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-semibold mb-6">Position Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="stat-label">Collateral (50%)</p>
            <p className="stat-value">
              ${stats ? (parseFloat(stats.collateral_usdc) / 1000).toFixed(1) : '0'}K
            </p>
            <p className="text-xs text-zerova-muted mt-1">Earning lending APY</p>
          </div>
          <div>
            <p className="stat-label">Perp Margin (45%)</p>
            <p className="stat-value">
              ${stats ? (parseFloat(stats.perp_notional) / 1000).toFixed(1) : '0'}K
            </p>
            <p className="text-xs text-zerova-muted mt-1">Short position notional</p>
          </div>
          <div>
            <p className="stat-label">Reserve (5%)</p>
            <p className="stat-value">
              ${stats ? (parseFloat(stats.reserve_balance) / 1000).toFixed(1) : '0'}K
            </p>
            <p className="text-xs text-zerova-muted mt-1">Withdrawal liquidity</p>
          </div>
          <div>
            <p className="stat-label">Margin Ratio</p>
            <p className={`stat-value ${
              stats && stats.margin_ratio > 0.3 ? 'text-zerova-success' : 'text-zerova-warning'
            }`}>
              {stats ? (stats.margin_ratio * 100).toFixed(1) : '0'}%
            </p>
            <p className="text-xs text-zerova-muted mt-1">Position health</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
