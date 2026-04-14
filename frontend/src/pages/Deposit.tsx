import { motion } from 'framer-motion'
import { Shield, TrendingUp, Zap } from 'lucide-react'
import { useVaultStats } from '@/hooks/useVaultStats'
import DepositWidget from '@/components/DepositWidget'

const features = [
  {
    icon: Shield,
    title: 'Delta-Neutral',
    description: 'Price movements fully hedged. Zero directional exposure.',
  },
  {
    icon: TrendingUp,
    title: 'Real Yield',
    description: 'Earn from funding rates, not inflationary token rewards.',
  },
  {
    icon: Zap,
    title: 'Automated',
    description: 'Rebalancing handled automatically by the protocol.',
  },
]

export default function Deposit() {
  const { data: stats } = useVaultStats()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Deposit into zvUSDC Vault</h1>
        <p className="text-zerova-muted mt-2">
          Earn delta-neutral yield on your USDC
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {features.map((feature, idx) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="card text-center"
          >
            <div className="w-10 h-10 rounded-lg bg-zerova-teal/10 flex items-center justify-center mx-auto mb-3">
              <feature.icon size={20} className="text-zerova-teal" />
            </div>
            <h3 className="font-semibold mb-1">{feature.title}</h3>
            <p className="text-sm text-zerova-muted">{feature.description}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <DepositWidget stats={stats ?? null} />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">How It Works</h3>
          <ol className="space-y-4">
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-zerova-teal/20 text-zerova-teal text-sm flex items-center justify-center">
                1
              </span>
              <div>
                <p className="font-medium">Deposit USDC</p>
                <p className="text-sm text-zerova-muted">
                  From Solana or bridge from other chains via Rhinofi
                </p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-zerova-teal/20 text-zerova-teal text-sm flex items-center justify-center">
                2
              </span>
              <div>
                <p className="font-medium">Receive zvUSDC</p>
                <p className="text-sm text-zerova-muted">
                  Vault shares representing your proportional claim
                </p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-zerova-teal/20 text-zerova-teal text-sm flex items-center justify-center">
                3
              </span>
              <div>
                <p className="font-medium">Earn Yield</p>
                <p className="text-sm text-zerova-muted">
                  NAV per share grows as funding fees accrue
                </p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-zerova-teal/20 text-zerova-teal text-sm flex items-center justify-center">
                4
              </span>
              <div>
                <p className="font-medium">Withdraw Anytime</p>
                <p className="text-sm text-zerova-muted">
                  Burn zvUSDC to receive USDC at current NAV
                </p>
              </div>
            </li>
          </ol>

          <div className="mt-6 pt-4 border-t border-zerova-border">
            <p className="text-xs text-zerova-muted">
              By depositing, you agree to the protocol terms. Minimum deposit: 10 USDC. 
              Protocol fee: 0.50% on yield. No entry or exit fees.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
