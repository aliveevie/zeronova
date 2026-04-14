import { useState } from 'react'
import { usePrivy } from '@privy-io/react-auth'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowUpFromLine, Loader2, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import { api } from '@/lib/api'
import type { VaultStats, UserPosition } from '@/types'

interface WithdrawWidgetProps {
  stats: VaultStats | null
  userPosition: UserPosition | null
}

export default function WithdrawWidget({ stats, userPosition }: WithdrawWidgetProps) {
  const { user, authenticated, login } = usePrivy()
  const queryClient = useQueryClient()
  const [amount, setAmount] = useState('')

  const withdrawMutation = useMutation({
    mutationFn: () =>
      api.vault.withdraw(user!.wallet!.address, parseFloat(amount)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vault'] })
      queryClient.invalidateQueries({ queryKey: ['user'] })
      setAmount('')
    },
  })

  const maxWithdraw = userPosition
    ? parseFloat(userPosition.zv_usdc_balance)
    : 0

  const estimatedUSDC =
    stats && amount
      ? (parseFloat(amount) * parseFloat(stats.nav_per_share)).toFixed(2)
      : '0.00'

  const handleWithdraw = () => {
    if (!authenticated) {
      login()
      return
    }
    withdrawMutation.mutate()
  }

  const handleMax = () => {
    setAmount(maxWithdraw.toString())
  }

  const isValidAmount =
    parseFloat(amount) > 0 && parseFloat(amount) <= maxWithdraw

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
        <ArrowUpFromLine size={20} className="text-zerova-teal" />
        Withdraw
      </h3>

      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="label mb-0">Amount (zvUSDC)</label>
            <button
              onClick={handleMax}
              className="text-xs text-zerova-teal hover:text-zerova-teal/80 transition-colors"
            >
              Max: {maxWithdraw.toFixed(4)}
            </button>
          </div>
          <div className="relative">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.0000"
              min="0"
              max={maxWithdraw}
              step="0.0001"
              className="input pr-20"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-zerova-muted text-sm">
              zvUSDC
            </span>
          </div>
        </div>

        <div className="p-4 bg-zerova-dark rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-zerova-muted">You will receive</span>
            <span className="font-mono">${estimatedUSDC} USDC</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-2">
            <span className="text-zerova-muted">NAV / Share</span>
            <span className="font-mono">
              ${stats ? parseFloat(stats.nav_per_share).toFixed(4) : '—'}
            </span>
          </div>
        </div>

        {withdrawMutation.isSuccess && withdrawMutation.data && (
          <div className="p-3 bg-zerova-success/10 border border-zerova-success/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle size={18} className="text-zerova-success" />
              <span className="text-sm text-zerova-success">Withdrawal queued!</span>
            </div>
            {withdrawMutation.data.queue_position > 0 && (
              <div className="flex items-center gap-2 text-xs text-zerova-muted">
                <Clock size={14} />
                <span>Queue position: #{withdrawMutation.data.queue_position}</span>
              </div>
            )}
          </div>
        )}

        {withdrawMutation.isError && (
          <div className="p-3 bg-zerova-danger/10 border border-zerova-danger/20 rounded-lg flex items-center gap-2">
            <AlertCircle size={18} className="text-zerova-danger" />
            <span className="text-sm text-zerova-danger">
              {(withdrawMutation.error as Error)?.message || 'Withdrawal failed'}
            </span>
          </div>
        )}

        <button
          onClick={handleWithdraw}
          disabled={withdrawMutation.isPending || (authenticated && !isValidAmount)}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {withdrawMutation.isPending ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Processing...
            </>
          ) : !authenticated ? (
            'Connect Wallet to Withdraw'
          ) : (
            'Withdraw'
          )}
        </button>
      </div>
    </motion.div>
  )
}
