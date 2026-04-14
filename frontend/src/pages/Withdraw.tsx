import { motion } from 'framer-motion'
import { Clock, Shield, AlertTriangle } from 'lucide-react'
import { useVaultStats } from '@/hooks/useVaultStats'
import { useUserPosition } from '@/hooks/useUserPosition'
import WithdrawWidget from '@/components/WithdrawWidget'

export default function Withdraw() {
  const { data: stats } = useVaultStats()
  const { data: userPosition } = useUserPosition()

  const hasPosition = userPosition && parseFloat(userPosition.zv_usdc_balance) > 0

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Withdraw from Vault</h1>
        <p className="text-zerova-muted mt-2">
          Burn zvUSDC to receive USDC at current NAV
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <WithdrawWidget stats={stats ?? null} userPosition={userPosition ?? null} />

        <div className="space-y-4">
          {hasPosition && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card bg-gradient-to-r from-zerova-teal/10 to-emerald-500/10 border-zerova-teal/20"
            >
              <h3 className="font-semibold mb-4">Your Position</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-zerova-muted">Balance</span>
                  <span className="font-mono">
                    {parseFloat(userPosition!.zv_usdc_balance).toFixed(4)} zvUSDC
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zerova-muted">Current Value</span>
                  <span className="font-mono">
                    ${parseFloat(userPosition!.usdc_current_value).toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zerova-muted">Total Deposited</span>
                  <span className="font-mono">
                    ${parseFloat(userPosition!.usdc_deposited).toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-zerova-border">
                  <span className="text-zerova-muted">Total Yield</span>
                  <span className={`font-mono ${
                    parseFloat(userPosition!.unrealised_yield) >= 0 
                      ? 'text-zerova-success' 
                      : 'text-zerova-danger'
                  }`}>
                    {parseFloat(userPosition!.unrealised_yield) >= 0 ? '+' : ''}
                    ${parseFloat(userPosition!.unrealised_yield).toFixed(2)}
                    <span className="text-sm text-zerova-muted ml-1">
                      ({userPosition!.yield_pct >= 0 ? '+' : ''}
                      {userPosition!.yield_pct.toFixed(2)}%)
                    </span>
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h3 className="font-semibold mb-4">Withdrawal Info</h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <Clock size={18} className="text-zerova-teal flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm">Processing Time</p>
                  <p className="text-xs text-zerova-muted">
                    Most withdrawals process within 15 minutes. Large withdrawals may queue.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Shield size={18} className="text-zerova-teal flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm">No Exit Fee</p>
                  <p className="text-xs text-zerova-muted">
                    Withdraw at any time with no penalty or exit fee.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <AlertTriangle size={18} className="text-zerova-warning flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm">Reserve Limits</p>
                  <p className="text-xs text-zerova-muted">
                    Large withdrawals may be queued if they exceed the liquidity reserve.
                  </p>
                </div>
              </li>
            </ul>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
