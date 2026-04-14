import { useState } from 'react'
import { motion } from 'framer-motion'
import { Users, Copy, CheckCircle } from 'lucide-react'
import type { ReferralInfo } from '@/types'

interface ReferralCardProps {
  referral: ReferralInfo | null
  isLoading: boolean
}

export default function ReferralCard({ referral, isLoading }: ReferralCardProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    if (!referral) return
    navigator.clipboard.writeText(referral.referral_link)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 w-32 bg-zerova-border rounded mb-4" />
        <div className="h-10 bg-zerova-border rounded" />
      </div>
    )
  }

  if (!referral) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex items-center gap-2 mb-4">
          <Users size={18} className="text-zerova-teal" />
          <h3 className="font-semibold">Referral Program</h3>
        </div>
        <p className="text-sm text-zerova-muted">
          Connect your wallet and make a deposit to get your referral link.
        </p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center gap-2 mb-4">
        <Users size={18} className="text-zerova-teal" />
        <h3 className="font-semibold">Referral Program</h3>
      </div>

      <div className="space-y-4">
        <div>
          <label className="label">Your Referral Link</label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={referral.referral_link}
              readOnly
              className="input text-sm"
            />
            <button
              onClick={handleCopy}
              className="btn-secondary p-3"
              title="Copy link"
            >
              {copied ? (
                <CheckCircle size={18} className="text-zerova-success" />
              ) : (
                <Copy size={18} />
              )}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-zerova-border">
          <div>
            <p className="text-xs text-zerova-muted">Earnings</p>
            <p className="font-mono text-lg">
              ${parseFloat(referral.total_earnings).toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-zerova-muted">Referred</p>
            <p className="font-mono text-lg">{referral.referred_count}</p>
          </div>
          <div>
            <p className="text-xs text-zerova-muted">Active</p>
            <p className="font-mono text-lg">{referral.active_referrals}</p>
          </div>
        </div>

        <p className="text-xs text-zerova-muted">
          Earn 5% of your referrals' yield for 90 days. Rewards paid in zvUSDC.
        </p>
      </div>
    </motion.div>
  )
}
