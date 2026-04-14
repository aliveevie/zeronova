export interface VaultStats {
  vault_id: string
  asset: string
  status: 'active' | 'transitioning' | 'parked'
  tvl_usdc: string
  nav_per_share: string
  total_zv_usdc_supply: string
  apy_7d: number
  current_funding_rate: number
  net_delta: string
  margin_ratio: number
  perp_notional: string
  collateral_usdc: string
  total_funding_received: string
  total_funding_paid: string
  protocol_fees: string
  reserve_balance: string
  updated_at: number
}

export interface NavHistoryPoint {
  timestamp: number
  nav_per_share: string
  total_assets: string
}

export interface NavHistoryResponse {
  vault_id: string
  window: string
  data: NavHistoryPoint[]
}

export interface Position {
  asset: string
  side: 'short' | 'long'
  notional: string
  entry_price: string
  unrealised_pnl: string
  margin_ratio: number
  funding_rate: number
}

export interface PositionsResponse {
  vault_id: string
  status: string
  positions: Position[]
}

export interface UserPosition {
  wallet_address: string
  zv_usdc_balance: string
  usdc_deposited: string
  usdc_current_value: string
  unrealised_yield: string
  yield_pct: number
  first_deposit_at: number
  last_action_at: number
  referral_code: string | null
  referral_earnings: string
}

export interface UserHistoryEvent {
  event_id: string
  event_type: 'deposit' | 'withdrawal'
  amount_usdc: string
  zv_usdc_amount: string
  nav_at_event: string
  timestamp: number
  tx_id: string | null
}

export interface ReferralInfo {
  referral_code: string
  referral_link: string
  total_earnings: string
  referred_count: number
  active_referrals: number
}

export interface SignalScore {
  asset: string
  frss: number
  funding_rate_estimate: number
  social_volume_24h: number
  sentiment_trend: 'improving' | 'stable' | 'deteriorating'
  confidence: number
  updated_at: number
}

export interface DepositResponse {
  event_id: string
  zv_usdc_minted: string
  nav_at_deposit: string
  tx_id: string
}

export interface WithdrawResponse {
  event_id: string
  usdc_returned: string
  nav_at_withdrawal: string
  queue_position: number
  estimated_ready_at: number
}
