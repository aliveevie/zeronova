"""
Position Manager.

Manages the lifecycle of Pacifica perpetual positions:
- Opening new short positions
- Closing/reducing positions
- Setting TP/SL for risk management
- Tracking position health
"""

import logging
from decimal import Decimal

from models.vault import VaultState, VaultStatus
from pacifica.client import ZerovaExecutor
from db.queries import upsert_vault_state
from config import settings

logger = logging.getLogger(__name__)


class PositionManager:
    def __init__(self, executor: ZerovaExecutor):
        self.executor = executor

    async def open_delta_neutral(
        self,
        vault: VaultState,
        deposit_amount: Decimal,
        oracle_price: Decimal,
    ) -> VaultState:
        """
        Open a delta-neutral position for new capital.

        Allocates 50% to collateral and opens a matching short perp.
        """
        collateral = deposit_amount * Decimal("0.50")
        perp_margin = deposit_amount * Decimal("0.45")

        # Short perp notional sized to match collateral exposure
        perp_notional_base = collateral / oracle_price

        try:
            result = await self.executor.open_short_position(
                symbol=vault.asset,
                notional_usdc=perp_margin,
            )
            logger.info(f"Short position opened: {result}")

            vault.perp_notional += perp_notional_base
            vault.perp_entry_price = oracle_price
            vault.collateral_usdc_value += collateral
            vault.net_delta = Decimal("0")  # delta neutral

            # Set protective stop-loss at 5% above entry
            sl_price = oracle_price * Decimal("1.05")
            await self.executor.set_position_tpsl(
                symbol=vault.asset,
                side="ask",
                sl_price=sl_price,
            )

        except Exception as e:
            logger.error(f"Failed to open delta-neutral position: {e}")
            raise

        return vault

    async def reduce_position(
        self,
        vault: VaultState,
        reduction_pct: Decimal,
    ) -> VaultState:
        """Reduce the perp position by a percentage (e.g., 0.25 for 25%)."""
        if vault.perp_notional <= 0:
            return vault

        close_amount = vault.perp_notional * reduction_pct

        try:
            result = await self.executor.close_short_position(
                symbol=vault.asset,
                amount=close_amount,
            )
            logger.info(f"Position reduced by {reduction_pct * 100}%: {result}")

            vault.perp_notional -= close_amount
            # Recalculate delta: collateral still exists but perp hedge reduced
            vault.net_delta = vault.collateral_usdc_value - (
                vault.perp_notional * vault.perp_entry_price
            )
        except Exception as e:
            logger.error(f"Failed to reduce position: {e}")
            raise

        return vault

    async def close_all_positions(self, vault: VaultState) -> VaultState:
        """Close all perp positions — used when transitioning to PARKED."""
        if vault.perp_notional <= 0:
            return vault

        try:
            result = await self.executor.close_short_position(
                symbol=vault.asset,
                amount=vault.perp_notional,
            )
            logger.info(f"All positions closed: {result}")

            vault.perp_notional = Decimal("0")
            vault.perp_entry_price = Decimal("0")
            vault.unrealised_perp_pnl = Decimal("0")
            vault.net_delta = vault.collateral_usdc_value
            vault.vault_status = VaultStatus.PARKED
        except Exception as e:
            logger.error(f"Failed to close all positions: {e}")
            raise

        return vault

    async def emergency_deleverage(self, vault: VaultState) -> VaultState:
        """Emergency reduction — close 50% of position immediately."""
        logger.warning(f"EMERGENCY DELEVERAGE triggered for {vault.vault_id}")
        return await self.reduce_position(vault, Decimal("0.50"))
