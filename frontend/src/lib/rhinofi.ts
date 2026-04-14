export interface BridgeParams {
  sourceChain: string
  amount: string
  vaultAddress: string
}

export interface BridgeResult {
  txHash: string
  estimatedTime: number
}

export async function bridgeDeposit(params: BridgeParams): Promise<BridgeResult> {
  const { sourceChain, amount, vaultAddress } = params

  if (sourceChain === 'solana') {
    return {
      txHash: '',
      estimatedTime: 0,
    }
  }

  const response = await fetch('/api/v1/bridge/initiate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from_chain: sourceChain,
      to_chain: 'solana',
      token: 'USDC',
      amount,
      recipient: vaultAddress,
    }),
  })

  if (!response.ok) {
    throw new Error('Bridge initiation failed')
  }

  const data = await response.json()
  return {
    txHash: data.tx_hash,
    estimatedTime: data.estimated_time_seconds,
  }
}

export function getSupportedChains() {
  return [
    { id: 'solana', name: 'Solana', icon: 'SOL', native: true },
    { id: 'ethereum', name: 'Ethereum', icon: 'ETH', native: false },
    { id: 'arbitrum', name: 'Arbitrum', icon: 'ARB', native: false },
    { id: 'optimism', name: 'Optimism', icon: 'OP', native: false },
    { id: 'polygon', name: 'Polygon', icon: 'MATIC', native: false },
    { id: 'base', name: 'Base', icon: 'BASE', native: false },
  ]
}

export function getChainConfig(chainId: string) {
  const chains = getSupportedChains()
  return chains.find((c) => c.id === chainId) ?? chains[0]
}
