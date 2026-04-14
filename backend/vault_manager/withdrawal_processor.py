"""
Withdrawal Processor.

Handles zvUSDC burn and USDC return:
1. Calculates USDC value at current NAV
2. Checks reserve liquidity
3. If insufficient reserve, queues withdrawal and flags partial perp unwind
4. Burns zvUSDC and returns USDC
"""

import logging
import time
from decimal import Decimal

from models.vault import VaultState
from models.user import UserPosition
from models.events import WithdrawalEvent
from db.queries import (
    get_vault_state,
    upsert_vault_state,
    get_user_position,
    upsert_user_position,
    insert_withdrawal_event,
)
from vault_manager.nav_engine import calculate_nav_per_share

logger = logging.getLogger(__name__)

WITHDRAWAL_COOLDOWN_MS = 15 * 60 * 1000  # 15 minutes


async def process_withdrawal(
    vault_id: str,
    wallet_address: str,
    zv_usdc_amount: Decimal,
) -> WithdrawalEvent:
    """
    Process a withdrawal request.

    Burns zvUSDC and returns proportional USDC at current NAV.
    """
    vault = await get_vault_state(vault_id)
    if vault is None:
        raise ValueError(f"Vault {vault_id} not found")

    user = await get_user_position(wallet_address)
    if user is None:
        raise ValueError(f"No position found for {wallet_address}")

    if zv_usdc_amount > user.zv_usdc_balance:
        raise ValueError(
            f"Insufficient zvUSDC: requested {zv_usdc_amount}, "
            f"available {user.zv_usdc_balance}"
        )

    now = int(time.time() * 1000)
    nav = calculate_nav_per_share(vault)
    usdc_to_return = zv_usdc_amount * nav

    # Check if reserve can cover withdrawal
    queue_position = 0
    estimated_ready_at = now
    if usdc_to_return > vault.reserve_balance:
        # Queue the withdrawal — vault manager will unwind perp on next cycle
        vault.pending_withdrawals += usdc_to_return
        queue_position = 1  # simplified — real impl would track queue
        estimated_ready_at = now + WITHDRAWAL_COOLDOWN_MS
        logger.warning(
            f"Withdrawal queued: {usdc_to_return} USDC exceeds reserve "
            f"{vault.reserve_balance}"
        )
    else:
        vault.reserve_balance -= usdc_to_return

    # Burn zvUSDC
    vault.total_zv_usdc_supply -= zv_usdc_amount
    vault.total_deposits_usdc -= usdc_to_return
    vault.updated_at = now
    await upsert_vault_state(vault)

    # Update user position
    user.zv_usdc_balance -= zv_usdc_amount
    user.usdc_current_value = user.zv_usdc_balance * nav
    user.unrealised_yield = user.usdc_current_value - user.usdc_deposited
    user.yield_pct = float(user.unrealised_yield / user.usdc_deposited) if user.usdc_deposited > 0 else 0.0
    user.last_action_at = now
    await upsert_user_position(user)

    # Record event
    event = WithdrawalEvent(
        wallet_address=wallet_address,
        zv_usdc_burned=zv_usdc_amount,
        usdc_returned=usdc_to_return,
        nav_at_withdrawal=nav,
        queue_position=queue_position,
        estimated_ready_at=estimated_ready_at,
    )
    await insert_withdrawal_event(event)

    logger.info(
        f"Withdrawal processed: {wallet_address} burned {zv_usdc_amount} zvUSDC, "
        f"returning {usdc_to_return} USDC at NAV {nav}"
    )
    return event
