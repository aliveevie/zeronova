"""
Vault API Routes.

Endpoints for vault stats, NAV history, deposits, withdrawals, and positions.
"""

import time
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from db.queries import get_vault_state, get_nav_history
from vault_manager.deposit_processor import process_deposit
from vault_manager.withdrawal_processor import process_withdrawal
from vault_manager.nav_engine import calculate_nav_per_share, estimate_apy
from pacifica.client import ZerovaExecutor

router = APIRouter(prefix="/api/v1/vault", tags=["vault"])

DEFAULT_VAULT_ID = "zerova-btc-v1"


# --- Request/Response Models ---

class DepositRequest(BaseModel):
    wallet: str
    amount_usdc: float
    referral_code: str | None = None
    source_chain: str = "solana"


class WithdrawRequest(BaseModel):
    wallet: str
    zv_usdc_amount: float


# --- Endpoints ---

@router.get("/stats")
async def vault_stats():
    """Returns TVL, APY (7d/30d), NAV/share, vault status, funding rate."""
    vault = await get_vault_state(DEFAULT_VAULT_ID)
    if not vault:
        raise HTTPException(404, "Vault not found")

    apy_7d = estimate_apy(vault, lookback_days=7)

    return {
        "vault_id": vault.vault_id,
        "asset": vault.asset,
        "status": vault.vault_status.value,
        "tvl_usdc": str(vault.total_deposits_usdc),
        "nav_per_share": str(vault.nav_per_share),
        "total_zv_usdc_supply": str(vault.total_zv_usdc_supply),
        "apy_7d": round(apy_7d * 100, 2),
        "current_funding_rate": vault.current_funding_rate,
        "net_delta": str(vault.net_delta),
        "margin_ratio": vault.margin_ratio,
        "perp_notional": str(vault.perp_notional),
        "collateral_usdc": str(vault.collateral_usdc_value),
        "total_funding_received": str(vault.total_funding_received),
        "total_funding_paid": str(vault.total_funding_paid),
        "protocol_fees": str(vault.protocol_fees_accrued),
        "reserve_balance": str(vault.reserve_balance),
        "updated_at": vault.updated_at,
    }


@router.get("/nav/history")
async def nav_history(window: str = "7d"):
    """Returns NAV-per-share history for charting."""
    now = int(time.time() * 1000)

    window_ms = {
        "7d": 7 * 24 * 60 * 60 * 1000,
        "30d": 30 * 24 * 60 * 60 * 1000,
        "all": now,
    }
    since = now - window_ms.get(window, window_ms["7d"])

    rows = await get_nav_history(DEFAULT_VAULT_ID, since)
    return {
        "vault_id": DEFAULT_VAULT_ID,
        "window": window,
        "data": [
            {
                "timestamp": r["timestamp"],
                "nav_per_share": str(r["nav_per_share"]),
                "total_assets": str(r["total_assets"]),
            }
            for r in rows
        ],
    }


@router.get("/positions")
async def vault_positions():
    """Returns active Pacifica positions, P&L, margin ratios."""
    vault = await get_vault_state(DEFAULT_VAULT_ID)
    if not vault:
        raise HTTPException(404, "Vault not found")

    positions = []
    if vault.perp_notional > 0:
        positions.append({
            "asset": vault.asset,
            "side": "short",
            "notional": str(vault.perp_notional),
            "entry_price": str(vault.perp_entry_price),
            "unrealised_pnl": str(vault.unrealised_perp_pnl),
            "margin_ratio": vault.margin_ratio,
            "funding_rate": vault.current_funding_rate,
        })

    return {
        "vault_id": DEFAULT_VAULT_ID,
        "status": vault.vault_status.value,
        "positions": positions,
    }


@router.post("/deposit")
async def deposit(req: DepositRequest):
    """Process a USDC deposit into the vault."""
    if req.amount_usdc <= 0:
        raise HTTPException(400, "Deposit amount must be positive")
    if req.amount_usdc < 10:
        raise HTTPException(400, "Minimum deposit is 10 USDC")

    try:
        executor = ZerovaExecutor()
        event = await process_deposit(
            vault_id=DEFAULT_VAULT_ID,
            wallet_address=req.wallet,
            amount_usdc=Decimal(str(req.amount_usdc)),
            source_chain=req.source_chain,
            referral_code=req.referral_code,
            executor=executor,
        )
        await executor.close()

        return {
            "event_id": event.event_id,
            "zv_usdc_minted": str(event.zv_usdc_minted),
            "nav_at_deposit": str(event.nav_at_deposit),
            "tx_id": event.tx_id,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/withdraw")
async def withdraw(req: WithdrawRequest):
    """Process a withdrawal (burn zvUSDC for USDC)."""
    if req.zv_usdc_amount <= 0:
        raise HTTPException(400, "Withdrawal amount must be positive")

    try:
        event = await process_withdrawal(
            vault_id=DEFAULT_VAULT_ID,
            wallet_address=req.wallet,
            zv_usdc_amount=Decimal(str(req.zv_usdc_amount)),
        )

        return {
            "event_id": event.event_id,
            "usdc_returned": str(event.usdc_returned),
            "nav_at_withdrawal": str(event.nav_at_withdrawal),
            "queue_position": event.queue_position,
            "estimated_ready_at": event.estimated_ready_at,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
