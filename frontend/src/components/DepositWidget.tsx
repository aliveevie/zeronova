import { useState } from 'react'
import { usePrivy } from '@privy-io/react-auth'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowDownToLine, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '@/lib/api'
import type { VaultStats } from '@/types'

interface DepositWidgetProps {
  stats: VaultStats | null
}

const CHAINS = [
  { id: 'solana', name: 'Solana', icon: 'SOL' },
  { id: 'ethereum', name: 'Ethereum', icon: 'ETH' },
  { id: 'arbitrum', name: 'Arbitrum', icon: 'ARB' },
  { id: 'base', name: 'Base', icon: 'BASE' },
]

export default function DepositWidget({ stats }: DepositWidgetProps) {
  const { user, authenticated, login } = usePrivy()
  const queryClient = useQueryClient()
  const [amount, setAmount] = useState('')
  const [chain, setChain] = useState('solana')
  const [referralCode, setReferralCode] = useState('')

  const depositMutation = useMutation({
    mutationFn: () =>
      api.vault.deposit(
        user!.wallet!.address,
        parseFloat(amount),
        referralCode || undefined,
        chain
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vault'] })
      queryClient.invalidateQueries({ queryKey: ['user'] })
      setAmount('')
    },
  })

  const estimatedZvUSDC =
    stats && amount
      ? (parseFloat(amount) / parseFloat(stats.nav_per_share)).toFixed(4)
      : '0.0000'

  const handleDeposit = () => {
    if (!authenticated) {
      login()
      return
    }
    depositMutation.mutate()
  }

  const isValidAmount = parseFloat(amount) >= 10

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
        <ArrowDownToLine size={20} className="text-zerova-teal" />
        Deposit USDC
      </h3>

      <div className="space-y-4">
        <div>
          <label className="label">Source Chain</label>
          <div className="grid grid-cols-4 gap-2">
            {CHAINS.map((c) => (
              <button
                key={c.id}
                onClick={() => setChain(c.id)}
                className={`p-2 rounded-lg border text-sm transition-colors ${
                  chain === c.id
                    ? 'border-zerova-teal bg-zerova-teal/10 text-zerova-teal'
                    : 'border-zerova-border hover:border-zerova-muted'
                }`}
              >
                {c.icon}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="label">Amount (USDC)</label>
          <div className="relative">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              min="10"
              step="0.01"
              className="input pr-16"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-zerova-muted text-sm">
              USDC
            </span>
          </div>
          {amount && !isValidAmount && (
            <p className="text-xs text-zerova-danger mt-1">Minimum deposit: 10 USDC</p>
          )}
        </div>

        <div>
          <label className="label">Referral Code (optional)</label>
          <input
            type="text"
            value={referralCode}
            onChange={(e) => setReferralCode(e.target.value)}
            placeholder="Enter referral code"
            className="input"
          />
        </div>

        <div className="p-4 bg-zerova-dark rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-zerova-muted">You will receive</span>
            <span className="font-mono">{estimatedZvUSDC} zvUSDC</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-2">
            <span className="text-zerova-muted">NAV / Share</span>
            <span className="font-mono">${stats ? parseFloat(stats.nav_per_share).toFixed(4) : '—'}</span>
          </div>
        </div>

        {depositMutation.isSuccess && (
          <div className="p-3 bg-zerova-success/10 border border-zerova-success/20 rounded-lg flex items-center gap-2">
            <CheckCircle size={18} className="text-zerova-success" />
            <span className="text-sm text-zerova-success">Deposit successful!</span>
          </div>
        )}

        {depositMutation.isError && (
          <div className="p-3 bg-zerova-danger/10 border border-zerova-danger/20 rounded-lg flex items-center gap-2">
            <AlertCircle size={18} className="text-zerova-danger" />
            <span className="text-sm text-zerova-danger">
              {(depositMutation.error as Error)?.message || 'Deposit failed'}
            </span>
          </div>
        )}

        <button
          onClick={handleDeposit}
          disabled={depositMutation.isPending || (authenticated && !isValidAmount)}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {depositMutation.isPending ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Processing...
            </>
          ) : !authenticated ? (
            'Connect Wallet to Deposit'
          ) : (
            'Deposit'
          )}
        </button>
      </div>
    </motion.div>
  )
}
