"""
NAV Engine.

Calculates Net Asset Value per zvUSDC share. Updated every 5 minutes
by the scheduler and on-demand after deposits/withdrawals.

NAV = collateral_value + unrealised_perp_pnl + accrued_funding_received
      - protocol_fees - accrued_funding_paid
"""

import logging
import time
from decimal import Decimal

from models.vault import VaultState
from db.queries import upsert_vault_state, insert_nav_snapshot

logger = logging.getLogger(__name__)


def calculate_nav_per_share(vault: VaultState) -> Decimal:
    """Calculate current NAV per zvUSDC share."""
    if vault.total_zv_usdc_supply <= 0:
        return Decimal("1.0")

    total_assets = (
        vault.collateral_usdc_value
        + vault.unrealised_perp_pnl
        + vault.total_funding_received
        - vault.total_funding_paid
        - vault.protocol_fees_accrued
    )

    return total_assets / vault.total_zv_usdc_supply


def calculate_total_assets(vault: VaultState) -> Decimal:
    """Calculate total assets under management."""
    return (
        vault.collateral_usdc_value
        + vault.unrealised_perp_pnl
        + vault.total_funding_received
        - vault.total_funding_paid
        - vault.protocol_fees_accrued
    )


def estimate_apy(vault: VaultState, lookback_days: int = 7) -> float:
    """Annualise the trailing yield over a lookback period."""
    if vault.nav_7d_ago <= 0:
        return 0.0

    trailing_yield = float(
        (vault.nav_per_share - vault.nav_7d_ago) / vault.nav_7d_ago
    )
    return trailing_yield * (365 / lookback_days)


async def recalculate(vault: VaultState) -> VaultState:
    """Recalculate NAV and persist snapshot."""
    vault.nav_per_share = calculate_nav_per_share(vault)
    vault.updated_at = int(time.time() * 1000)

    total_assets = calculate_total_assets(vault)

    # Persist updated state and NAV snapshot
    await upsert_vault_state(vault)
    await insert_nav_snapshot(vault.vault_id, vault.nav_per_share, total_assets)

    logger.info(
        f"NAV recalculated for {vault.vault_id}: "
        f"{vault.nav_per_share} (total_assets={total_assets})"
    )
    return vault
