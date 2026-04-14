import { usePrivy } from '@privy-io/react-auth'
import { motion } from 'framer-motion'
import { ArrowDownToLine, ArrowUpFromLine, Wallet } from 'lucide-react'
import { useUserPosition } from '@/hooks/useUserPosition'
import { useUserHistory } from '@/hooks/useUserHistory'
import { useReferral } from '@/hooks/useReferral'
import ReferralCard from '@/components/ReferralCard'

export default function Portfolio() {
  const { authenticated, login } = usePrivy()
  const { data: position, isLoading: positionLoading } = useUserPosition()
  const { data: history, isLoading: historyLoading } = useUserHistory()
  const { data: referral, isLoading: referralLoading } = useReferral()

  if (!authenticated) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <div className="w-16 h-16 rounded-full bg-zerova-card flex items-center justify-center mx-auto mb-6">
          <Wallet size={32} className="text-zerova-muted" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Connect Your Wallet</h1>
        <p className="text-zerova-muted mb-6">
          Connect your wallet to view your portfolio and transaction history.
        </p>
        <button onClick={() => login()} className="btn-primary">
          Connect Wallet
        </button>
      </div>
    )
  }

  if (positionLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-48 bg-zerova-border rounded" />
          <div className="card h-40" />
          <div className="card h-60" />
        </div>
      </div>
    )
  }

  const hasPosition = position && parseFloat(position.zv_usdc_balance) > 0

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Your Portfolio</h1>
        <p className="text-zerova-muted mt-1">
          Track your zvUSDC holdings and yield
        </p>
      </div>

      {hasPosition ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-zerova-teal/10 to-emerald-500/10 border-zerova-teal/20"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="stat-label">zvUSDC Balance</p>
              <p className="stat-value">{parseFloat(position!.zv_usdc_balance).toFixed(4)}</p>
            </div>
            <div>
              <p className="stat-label">Current Value</p>
              <p className="stat-value">${parseFloat(position!.usdc_current_value).toFixed(2)}</p>
            </div>
            <div>
              <p className="stat-label">Total Deposited</p>
              <p className="stat-value">${parseFloat(position!.usdc_deposited).toFixed(2)}</p>
            </div>
            <div>
              <p className="stat-label">Total Yield</p>
              <p className={`stat-value ${
                parseFloat(position!.unrealised_yield) >= 0 
                  ? 'text-zerova-success' 
                  : 'text-zerova-danger'
              }`}>
                {parseFloat(position!.unrealised_yield) >= 0 ? '+' : ''}
                ${parseFloat(position!.unrealised_yield).toFixed(2)}
              </p>
            </div>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card text-center py-12"
        >
          <p className="text-zerova-muted mb-4">You don't have any zvUSDC yet.</p>
          <a href="/deposit" className="btn-primary inline-flex items-center gap-2">
            <ArrowDownToLine size={16} />
            Make Your First Deposit
          </a>
        </motion.div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Transaction History</h3>
          {historyLoading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-12 bg-zerova-border rounded" />
              ))}
            </div>
          ) : !history || history.length === 0 ? (
            <p className="text-zerova-muted text-center py-8">
              No transactions yet
            </p>
          ) : (
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {history.map((event) => (
                <div
                  key={event.event_id}
                  className="flex items-center justify-between p-3 bg-zerova-dark rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      event.event_type === 'deposit' 
                        ? 'bg-zerova-success/20 text-zerova-success'
                        : 'bg-zerova-warning/20 text-zerova-warning'
                    }`}>
                      {event.event_type === 'deposit' ? (
                        <ArrowDownToLine size={16} />
                      ) : (
                        <ArrowUpFromLine size={16} />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium capitalize">{event.event_type}</p>
                      <p className="text-xs text-zerova-muted">
                        {new Date(event.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-mono">
                      ${parseFloat(event.amount_usdc).toFixed(2)}
                    </p>
                    <p className="text-xs text-zerova-muted font-mono">
                      {parseFloat(event.zv_usdc_amount).toFixed(4)} zvUSDC
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <ReferralCard referral={referral ?? null} isLoading={referralLoading} />
      </div>
    </div>
  )
}
