import { useState, useEffect } from 'react'
import { usePrivy } from '@privy-io/react-auth'
import { motion } from 'framer-motion'
import { Shield, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import {
  ZEROVA_BUILDER_CODE,
  BUILDER_FEE_RATE,
  createBuilderApprovalPayload,
  checkBuilderApproval,
  submitBuilderApproval,
  type ApprovalStatus,
} from '@/lib/pacifica'

interface BuilderApprovalProps {
  onApproved?: () => void
}

export default function BuilderApproval({ onApproved }: BuilderApprovalProps) {
  const { user, signMessage, authenticated } = usePrivy()
  const [status, setStatus] = useState<ApprovalStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSigning, setIsSigning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wallet = user?.wallet?.address

  useEffect(() => {
    if (!wallet) {
      setIsLoading(false)
      return
    }

    checkBuilderApproval(wallet)
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setIsLoading(false))
  }, [wallet])

  const handleApprove = async () => {
    if (!wallet || !signMessage) return

    setIsSigning(true)
    setError(null)

    try {
      const payload = createBuilderApprovalPayload()
      const message = JSON.stringify(payload, null, 2)

      const signResult = await signMessage({ message })
      const signature = typeof signResult === 'string' ? signResult : signResult.signature

      const submitResult = await submitBuilderApproval(wallet, signature, payload)

      if (submitResult.success) {
        setStatus({
          approved: true,
          builder_code: ZEROVA_BUILDER_CODE,
          max_fee_rate: BUILDER_FEE_RATE,
          approved_at: Date.now(),
        })
        onApproved?.()
      } else {
        setError(submitResult.error || 'Approval failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signature rejected')
    } finally {
      setIsSigning(false)
    }
  }

  if (!authenticated || !wallet) {
    return null
  }

  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-20 bg-zerova-border rounded" />
      </div>
    )
  }

  if (status?.approved) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 bg-zerova-success/10 border border-zerova-success/20 rounded-lg flex items-center gap-3"
      >
        <CheckCircle size={20} className="text-zerova-success" />
        <div>
          <p className="text-sm font-medium text-zerova-success">Builder Code Approved</p>
          <p className="text-xs text-zerova-muted">
            Zerova can place orders on your behalf with a {parseFloat(BUILDER_FEE_RATE) * 100}% builder fee.
          </p>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card border-zerova-warning/50"
    >
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-lg bg-zerova-warning/20 flex items-center justify-center flex-shrink-0">
          <Shield size={20} className="text-zerova-warning" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold mb-1">Approve Builder Code</h4>
          <p className="text-sm text-zerova-muted mb-4">
            To deposit into the vault, you need to authorize Zerova to place orders on Pacifica on your behalf. 
            This is a one-time approval that you can revoke at any time.
          </p>

          <div className="p-3 bg-zerova-dark rounded-lg mb-4 space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-zerova-muted">Builder Code</span>
              <span className="font-mono">{ZEROVA_BUILDER_CODE}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zerova-muted">Max Fee Rate</span>
              <span className="font-mono">{parseFloat(BUILDER_FEE_RATE) * 100}%</span>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-zerova-danger/10 border border-zerova-danger/20 rounded-lg flex items-center gap-2 mb-4">
              <AlertCircle size={16} className="text-zerova-danger" />
              <span className="text-sm text-zerova-danger">{error}</span>
            </div>
          )}

          <button
            onClick={handleApprove}
            disabled={isSigning}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {isSigning ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Signing...
              </>
            ) : (
              <>
                <Shield size={16} />
                Approve Builder Code
              </>
            )}
          </button>
        </div>
      </div>
    </motion.div>
  )
}
