const FUUL_PROJECT_ID = import.meta.env.VITE_FUUL_PROJECT_ID
const FUUL_API_KEY = import.meta.env.VITE_FUUL_API_KEY
const BASE_URL = 'https://api.fuul.xyz/v1'

async function fuulFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': FUUL_API_KEY || '',
      'X-Project-ID': FUUL_PROJECT_ID || '',
      ...options?.headers,
    },
  })

  if (!res.ok) {
    throw new Error(`Fuul API error: ${res.status}`)
  }

  return res.json()
}

export interface ReferralLinkResponse {
  referral_code: string
  referral_link: string
}

export async function generateReferralLink(walletAddress: string): Promise<string> {
  const data = await fuulFetch<ReferralLinkResponse>('/referrals/generate', {
    method: 'POST',
    body: JSON.stringify({
      referrer: walletAddress,
      campaign: 'zerova-depositor-v1',
    }),
  })

  return data.referral_link
}

export interface ConversionParams {
  wallet: string
  referralCode: string | null
  eventType: 'deposit' | 'withdrawal'
  value: number
}

export async function trackConversion(params: ConversionParams): Promise<void> {
  await fuulFetch('/conversions/track', {
    method: 'POST',
    body: JSON.stringify({
      wallet: params.wallet,
      referral_code: params.referralCode,
      event_type: params.eventType,
      value: params.value,
      currency: 'USDC',
    }),
  })
}

export interface ReferralStats {
  total_referrals: number
  active_referrals: number
  total_earnings: string
  pending_earnings: string
}

export async function getReferralStats(walletAddress: string): Promise<ReferralStats> {
  return fuulFetch<ReferralStats>(`/referrals/${walletAddress}/stats`)
}

export function getReferralCodeFromUrl(): string | null {
  if (typeof window === 'undefined') return null
  const params = new URLSearchParams(window.location.search)
  return params.get('ref')
}
