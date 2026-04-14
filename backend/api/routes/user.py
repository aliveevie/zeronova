"""
User API Routes.

Endpoints for user position, history, and referral data.
"""

from fastapi import APIRouter, HTTPException

from db.queries import (
    get_user_position,
    get_user_deposit_history,
    get_user_withdrawal_history,
)

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.get("/{wallet}/position")
async def user_position(wallet: str):
    """Returns the user's current zvUSDC position and yield."""
    pos = await get_user_position(wallet)
    if not pos:
        raise HTTPException(404, "No position found for this wallet")

    return {
        "wallet_address": pos.wallet_address,
        "zv_usdc_balance": str(pos.zv_usdc_balance),
        "usdc_deposited": str(pos.usdc_deposited),
        "usdc_current_value": str(pos.usdc_current_value),
        "unrealised_yield": str(pos.unrealised_yield),
        "yield_pct": round(pos.yield_pct * 100, 2),
        "first_deposit_at": pos.first_deposit_at,
        "last_action_at": pos.last_action_at,
        "referral_code": pos.referral_code,
        "referral_earnings": str(pos.referral_earnings),
    }


@router.get("/{wallet}/history")
async def user_history(wallet: str):
    """Returns deposit and withdrawal event history for a wallet."""
    deposits = await get_user_deposit_history(wallet)
    withdrawals = await get_user_withdrawal_history(wallet)

    return {
        "wallet": wallet,
        "deposits": [
            {
                "event_id": d["event_id"],
                "amount_usdc": str(d["amount_usdc"]),
                "zv_usdc_minted": str(d["zv_usdc_minted"]),
                "nav_at_deposit": str(d["nav_at_deposit"]),
                "source_chain": d["source_chain"],
                "tx_id": d["tx_id"],
                "timestamp": d["timestamp"],
            }
            for d in deposits
        ],
        "withdrawals": [
            {
                "event_id": w["event_id"],
                "zv_usdc_burned": str(w["zv_usdc_burned"]),
                "usdc_returned": str(w["usdc_returned"]),
                "nav_at_withdrawal": str(w["nav_at_withdrawal"]),
                "tx_id": w["tx_id"],
                "timestamp": w["timestamp"],
            }
            for w in withdrawals
        ],
    }


@router.get("/{wallet}/referral")
async def user_referral(wallet: str):
    """Returns referral info: code, earnings, referred count."""
    pos = await get_user_position(wallet)
    if not pos:
        raise HTTPException(404, "No position found for this wallet")

    return {
        "wallet": wallet,
        "referral_code": pos.referral_code,
        "referral_earnings": str(pos.referral_earnings),
    }
