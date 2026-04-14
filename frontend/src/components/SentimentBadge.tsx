import { motion } from 'framer-motion'
import { Brain, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import type { SignalScore } from '@/types'

interface SentimentBadgeProps {
  signal: SignalScore | null
  isLoading: boolean
}

export default function SentimentBadge({ signal, isLoading }: SentimentBadgeProps) {
  if (isLoading || !signal) {
    return (
      <div className="card animate-pulse">
        <div className="h-5 w-32 bg-zerova-border rounded mb-3" />
        <div className="h-8 w-20 bg-zerova-border rounded" />
      </div>
    )
  }

  const getSentimentColor = (frss: number) => {
    if (frss >= 0.75) return 'text-zerova-success'
    if (frss >= 0.5) return 'text-emerald-400'
    if (frss >= 0.3) return 'text-zerova-warning'
    return 'text-zerova-danger'
  }

  const getSentimentLabel = (frss: number) => {
    if (frss >= 0.75) return 'Strong Bullish'
    if (frss >= 0.5) return 'Mild Bullish'
    if (frss >= 0.3) return 'Neutral'
    return 'Bearish'
  }

  const TrendIcon = {
    improving: TrendingUp,
    stable: Minus,
    deteriorating: TrendingDown,
  }[signal.sentiment_trend]

  const trendColors = {
    improving: 'text-zerova-success',
    stable: 'text-zerova-muted',
    deteriorating: 'text-zerova-danger',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="card"
    >
      <div className="flex items-center gap-2 mb-4">
        <Brain size={18} className="text-zerova-teal" />
        <h3 className="font-semibold">Elfa AI Signal</h3>
      </div>

      <div className="space-y-4">
        <div>
          <p className="stat-label">Funding Sentiment Score</p>
          <p className={`stat-value ${getSentimentColor(signal.frss)}`}>
            {(signal.frss * 100).toFixed(0)}%
          </p>
          <p className="text-sm text-zerova-muted mt-1">{getSentimentLabel(signal.frss)}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-zerova-border">
          <div>
            <p className="text-xs text-zerova-muted">Trend</p>
            <p className={`flex items-center gap-1 text-sm ${trendColors[signal.sentiment_trend]}`}>
              <TrendIcon size={14} />
              <span className="capitalize">{signal.sentiment_trend}</span>
            </p>
          </div>
          <div>
            <p className="text-xs text-zerova-muted">Confidence</p>
            <p className="text-sm">{(signal.confidence * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-xs text-zerova-muted">Est. Funding</p>
            <p className={`text-sm ${signal.funding_rate_estimate >= 0 ? 'text-zerova-success' : 'text-zerova-danger'}`}>
              {(signal.funding_rate_estimate * 100).toFixed(4)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-zerova-muted">Social Vol (24h)</p>
            <p className="text-sm">{signal.social_volume_24h.toLocaleString()}</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
