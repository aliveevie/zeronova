import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface FundingRateGaugeProps {
  rate: number
  isLoading?: boolean
}

export default function FundingRateGauge({ rate, isLoading }: FundingRateGaugeProps) {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-5 w-32 bg-zerova-border rounded mb-3" />
        <div className="h-8 w-24 bg-zerova-border rounded" />
      </div>
    )
  }

  const ratePercent = rate * 100
  const isPositive = rate > 0
  const isNeutral = Math.abs(rate) < 0.0001

  const getColor = () => {
    if (isNeutral) return 'text-zerova-muted'
    return isPositive ? 'text-zerova-success' : 'text-zerova-danger'
  }

  const getIcon = () => {
    if (isNeutral) return Minus
    return isPositive ? TrendingUp : TrendingDown
  }

  const Icon = getIcon()

  const gaugePosition = Math.min(100, Math.max(0, (rate + 0.01) / 0.02 * 100))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <p className="text-sm text-zerova-muted mb-2">Funding Rate (8h)</p>
      <div className={`text-2xl font-mono font-semibold flex items-center gap-2 ${getColor()}`}>
        <Icon size={24} />
        {isPositive ? '+' : ''}{ratePercent.toFixed(4)}%
      </div>

      <div className="mt-4">
        <div className="relative h-2 bg-zerova-dark rounded-full overflow-hidden">
          <div
            className="absolute left-0 top-0 h-full bg-gradient-to-r from-zerova-danger via-zerova-warning to-zerova-success"
            style={{ width: '100%' }}
          />
          <motion.div
            initial={{ left: '50%' }}
            animate={{ left: `${gaugePosition}%` }}
            transition={{ type: 'spring', stiffness: 100 }}
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full border-2 border-zerova-dark"
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-zerova-muted">
          <span>Shorts pay</span>
          <span>Longs pay</span>
        </div>
      </div>

      <p className="text-xs text-zerova-muted mt-4">
        {isPositive
          ? 'Positive funding: Longs pay shorts. Favorable for the vault.'
          : isNeutral
          ? 'Neutral funding rate.'
          : 'Negative funding: Shorts pay longs. Vault may transition to parked state.'}
      </p>
    </motion.div>
  )
}
