export const ZEROVA_BUILDER_CODE = 'ZEROVA01'
export const BUILDER_FEE_RATE = '0.0005'

export interface BuilderApprovalPayload {
  type: 'approve_builder_code'
  data: {
    builder_code: string
    max_fee_rate: string
  }
  timestamp: number
  nonce: string
}

export function createBuilderApprovalPayload(): BuilderApprovalPayload {
  return {
    type: 'approve_builder_code',
    data: {
      builder_code: ZEROVA_BUILDER_CODE,
      max_fee_rate: BUILDER_FEE_RATE,
    },
    timestamp: Date.now(),
    nonce: crypto.randomUUID(),
  }
}

export interface ApprovalStatus {
  approved: boolean
  builder_code: string | null
  max_fee_rate: string | null
  approved_at: number | null
}

export async function checkBuilderApproval(walletAddress: string): Promise<ApprovalStatus> {
  const res = await fetch(`/api/v1/builder/approval/${walletAddress}`)

  if (!res.ok) {
    return {
      approved: false,
      builder_code: null,
      max_fee_rate: null,
      approved_at: null,
    }
  }

  return res.json()
}

export async function submitBuilderApproval(
  walletAddress: string,
  signature: string,
  payload: BuilderApprovalPayload
): Promise<{ success: boolean; error?: string }> {
  const res = await fetch('/api/v1/builder/approve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet: walletAddress,
      signature,
      payload,
    }),
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    return { success: false, error: data.detail || 'Approval failed' }
  }

  return { success: true }
}

export async function revokeBuilderApproval(
  walletAddress: string,
  signature: string
): Promise<{ success: boolean; error?: string }> {
  const res = await fetch('/api/v1/builder/revoke', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet: walletAddress,
      signature,
    }),
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    return { success: false, error: data.detail || 'Revocation failed' }
  }

  return { success: true }
}
