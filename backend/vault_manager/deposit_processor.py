"""
Deposit Processor.

Handles incoming USDC deposits:
1. Validates deposit
2. Allocates capital: 50% collateral, 45% perp margin, 5% reserve
3. Opens short perp via ZerovaExecutor
4. Mints zvUSDC at current NAV
5. Records deposit event
"""

import logging
import time
from decimal import Decimal

from models.vault import VaultState, VaultStatus
from models.user import UserPosition
from models.events import DepositEvent
from db.queries import (
    get_vault_state,
    upsert_vault_state,
    get_user_position,
    upsert_user_position,
    insert_deposit_event,
)
from vault_manager.nav_engine import calculate_nav_per_share
from pacifica.client import ZerovaExecutor

logger = logging.getLogger(__name__)

# Capital allocation ratios
COLLATERAL_RATIO = Decimal("0.50")
PERP_MARGIN_RATIO = Decimal("0.45")
RESERVE_RATIO = Decimal("0.05")


async def process_deposit(
    vault_id: str,
    wallet_address: str,
    amount_usdc: Decimal,
    source_chain: str = "solana",
    referral_code: str | None = None,
    executor: ZerovaExecutor | None = None,
) -> DepositEvent:
    """
    Process a user deposit into the vault.

    Returns the deposit event with mint details.
    """
    vault = await get_vault_state(vault_id)
    if vault is None:
        raise ValueError(f"Vault {vault_id} not found")

    if vault.vault_status == VaultStatus.TRANSITIONING:
        raise ValueError("Vault is transitioning, deposits temporarily paused")

    # Calculate allocations
    collateral_amount = amount_usdc * COLLATERAL_RATIO
    perp_margin = amount_usdc * PERP_MARGIN_RATIO
    reserve_amount = amount_usdc * RESERVE_RATIO

    # Mint zvUSDC at current NAV
    nav = calculate_nav_per_share(vault)
    zv_usdc_minted = amount_usdc / nav

    # Open short perp position if vault is active
    tx_id = ""
    if vault.vault_status == VaultStatus.ACTIVE and executor:
        try:
            result = await executor.open_short_position(
                symbol=vault.asset,
                notional_usdc=perp_margin,
            )
            tx_id = result.get("order_id", "")
            logger.info(f"Opened short position: {result}")
        except Exception as e:
            logger.error(f"Failed to open perp position: {e}")
            # Continue with deposit — capital goes to reserve until next rebalance

    # Update vault state
    now = int(time.time() * 1000)
    vault.total_deposits_usdc += amount_usdc
    vault.total_zv_usdc_supply += zv_usdc_minted
    vault.collateral_usdc_value += collateral_amount
    vault.reserve_balance += reserve_amount
    vault.nav_per_share = nav
    vault.updated_at = now
    await upsert_vault_state(vault)

    # Update user position
    user = await get_user_position(wallet_address)
    if user is None:
        user = UserPosition(
            wallet_address=wallet_address,
            first_deposit_at=now,
            referral_code=referral_code,
        )
    user.zv_usdc_balance += zv_usdc_minted
    user.usdc_deposited += amount_usdc
    user.usdc_current_value = user.zv_usdc_balance * nav
    user.unrealised_yield = user.usdc_current_value - user.usdc_deposited
    user.yield_pct = float(user.unrealised_yield / user.usdc_deposited) if user.usdc_deposited > 0 else 0.0
    user.last_action_at = now
    await upsert_user_position(user)

    # Record event
    event = DepositEvent(
        wallet_address=wallet_address,
        amount_usdc=amount_usdc,
        zv_usdc_minted=zv_usdc_minted,
        nav_at_deposit=nav,
        source_chain=source_chain,
        referral_code=referral_code,
        tx_id=tx_id,
    )
    await insert_deposit_event(event)

    logger.info(
        f"Deposit processed: {wallet_address} deposited {amount_usdc} USDC, "
        f"minted {zv_usdc_minted} zvUSDC at NAV {nav}"
    )
    return event
