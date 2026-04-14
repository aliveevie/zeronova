import { motion } from 'framer-motion'
import { TrendingDown, AlertTriangle } from 'lucide-react'
import type { Position } from '@/types'

interface PositionTableProps {
  positions: Position[]
  isLoading: boolean
}

export default function PositionTable({ positions, isLoading }: PositionTableProps) {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 w-40 bg-zerova-border rounded mb-4" />
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="h-12 bg-zerova-border rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (positions.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <h3 className="text-lg font-semibold mb-4">Active Positions</h3>
        <p className="text-zerova-muted text-center py-8">
          No active positions — vault is parked
        </p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="card"
    >
      <h3 className="text-lg font-semibold mb-4">Active Positions</h3>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-zerova-muted border-b border-zerova-border">
              <th className="pb-3 font-medium">Asset</th>
              <th className="pb-3 font-medium">Side</th>
              <th className="pb-3 font-medium text-right">Notional</th>
              <th className="pb-3 font-medium text-right">Entry</th>
              <th className="pb-3 font-medium text-right">PnL</th>
              <th className="pb-3 font-medium text-right">Margin</th>
              <th className="pb-3 font-medium text-right">Funding</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos, idx) => (
              <tr key={idx} className="border-b border-zerova-border last:border-0">
                <td className="py-4 font-medium">{pos.asset}</td>
                <td className="py-4">
                  <span className="flex items-center gap-1 text-zerova-danger">
                    <TrendingDown size={14} />
                    Short
                  </span>
                </td>
                <td className="py-4 text-right font-mono">
                  ${parseFloat(pos.notional).toLocaleString()}
                </td>
                <td className="py-4 text-right font-mono">
                  ${parseFloat(pos.entry_price).toLocaleString()}
                </td>
                <td className={`py-4 text-right font-mono ${
                  parseFloat(pos.unrealised_pnl) >= 0 ? 'text-zerova-success' : 'text-zerova-danger'
                }`}>
                  {parseFloat(pos.unrealised_pnl) >= 0 ? '+' : ''}
                  ${parseFloat(pos.unrealised_pnl).toFixed(2)}
                </td>
                <td className="py-4 text-right">
                  <span className={`flex items-center justify-end gap-1 ${
                    pos.margin_ratio > 0.3 ? 'text-zerova-success' : 
                    pos.margin_ratio > 0.2 ? 'text-zerova-warning' : 'text-zerova-danger'
                  }`}>
                    {pos.margin_ratio < 0.25 && <AlertTriangle size={14} />}
                    {(pos.margin_ratio * 100).toFixed(1)}%
                  </span>
                </td>
                <td className={`py-4 text-right font-mono ${
                  pos.funding_rate >= 0 ? 'text-zerova-success' : 'text-zerova-danger'
                }`}>
                  {(pos.funding_rate * 100).toFixed(4)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}
