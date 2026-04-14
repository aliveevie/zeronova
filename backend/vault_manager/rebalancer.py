"""
Vault Rebalancer.

Evaluates rebalancing conditions every epoch (1 hour) using a hysteresis
state machine to prevent thrashing on funding rate oscillation.

State transitions require conditions to hold for MIN_HOLD_EPOCHS (default: 3)
before executing.

States: ACTIVE -> TRANSITIONING -> PARKED
"""

import logging
import time

from models.vault import VaultState, VaultStatus, RebalanceTrigger
from signal_engine.elfa_client import SignalScore
from signal_engine.scorer import SignalScorer
from signal_engine.cache import get_cached_signal, cache_signal
from vault_manager.position_manager import PositionManager
from db.queries import upsert_vault_state
from config import settings
from decimal import Decimal

logger = logging.getLogger(__name__)

# FRSS thresholds for signal-driven rebalancing
FRSS_REDUCE_THRESHOLD = 0.50   # Below this: reduce exposure by 25%
FRSS_EXIT_THRESHOLD = 0.30     # Below this: full exit to PARKED


def evaluate_rebalance(
    state: VaultState, signal: SignalScore | None
) -> RebalanceTrigger | None:
    """Evaluate all rebalance triggers and return the highest-priority one."""
    if abs(state.net_delta) > Decimal(str(settings.vault_delta_drift_threshold)):
        return RebalanceTrigger.DELTA_DRIFT

    if state.current_funding_rate < settings.vault_funding_rate_floor:
        return RebalanceTrigger.FUNDING_FLIP

    if state.margin_ratio < settings.vault_margin_safe_floor:
        return RebalanceTrigger.MARGIN_THRESHOLD

    if signal and signal.frss < FRSS_EXIT_THRESHOLD:
        return RebalanceTrigger.SENTIMENT_EXIT

    if state.pending_withdrawals > state.reserve_balance:
        return RebalanceTrigger.WITHDRAWAL_QUEUE

    return None


class Rebalancer:
    def __init__(
        self,
        position_manager: PositionManager,
        signal_scorer: SignalScorer,
    ):
        self.position_manager = position_manager
        self.signal_scorer = signal_scorer

    async def evaluate(self, vault: VaultState) -> VaultState:
        """Run full rebalance evaluation cycle."""
        # Fetch signal (from cache or fresh)
        signal = await get_cached_signal(vault.asset)
        if signal is None:
            try:
                signal = await self.signal_scorer.compute_frss(vault.asset)
                await cache_signal(signal)
            except Exception as e:
                logger.warning(f"Failed to compute signal: {e}")

        trigger = evaluate_rebalance(vault, signal)

        if trigger is None:
            # Reset transition counter if no trigger
            if vault.transition_epoch_count > 0:
                vault.transition_epoch_count = 0
                await upsert_vault_state(vault)
            return vault

        logger.info(f"Rebalance trigger: {trigger.value} for {vault.vault_id}")

        # Hysteresis: require condition to hold for MIN_HOLD_EPOCHS
        vault.transition_epoch_count += 1

        if vault.transition_epoch_count < settings.vault_min_hold_epochs:
            logger.info(
                f"Hysteresis: {vault.transition_epoch_count}/{settings.vault_min_hold_epochs} "
                f"epochs for {trigger.value}"
            )
            await upsert_vault_state(vault)
            return vault

        # Execute rebalance action
        vault = await self._execute_rebalance(vault, trigger, signal)
        vault.last_rebalance_at = int(time.time() * 1000)
        vault.transition_epoch_count = 0
        await upsert_vault_state(vault)

        return vault

    async def _execute_rebalance(
        self,
        vault: VaultState,
        trigger: RebalanceTrigger,
        signal: SignalScore | None,
    ) -> VaultState:
        """Execute the appropriate rebalance action for a trigger."""

        if trigger == RebalanceTrigger.MARGIN_THRESHOLD:
            # Emergency: reduce position to restore margin
            logger.warning("Margin threshold hit — emergency deleverage")
            vault = await self.position_manager.emergency_deleverage(vault)

        elif trigger == RebalanceTrigger.FUNDING_FLIP:
            # Funding went negative — close perp and park
            logger.info("Funding rate negative — transitioning to PARKED")
            vault.vault_status = VaultStatus.TRANSITIONING
            vault = await self.position_manager.close_all_positions(vault)

        elif trigger == RebalanceTrigger.SENTIMENT_EXIT:
            # Elfa AI signals bearish — exit to safety
            if signal and signal.frss < FRSS_EXIT_THRESHOLD:
                logger.info(f"Sentiment exit (FRSS={signal.frss}) — parking vault")
                vault.vault_status = VaultStatus.TRANSITIONING
                vault = await self.position_manager.close_all_positions(vault)
            elif signal and signal.frss < FRSS_REDUCE_THRESHOLD:
                logger.info(f"Sentiment reduce (FRSS={signal.frss}) — reducing 25%")
                vault = await self.position_manager.reduce_position(
                    vault, Decimal("0.25")
                )

        elif trigger == RebalanceTrigger.DELTA_DRIFT:
            # Delta drifted — rebalance perp to restore Δ=0
            logger.info("Delta drift — rebalancing to restore hedge")
            # Simplified: reduce the larger side
            vault = await self.position_manager.reduce_position(
                vault, Decimal("0.10")
            )

        elif trigger == RebalanceTrigger.WITHDRAWAL_QUEUE:
            # Pending withdrawals exceed reserve — unwind some perp
            logger.info("Withdrawal queue — unwinding position for liquidity")
            vault = await self.position_manager.reduce_position(
                vault, Decimal("0.20")
            )

        return vault

    async def check_resume(self, vault: VaultState) -> VaultState:
        """Check if a PARKED vault should resume active trading."""
        if vault.vault_status != VaultStatus.PARKED:
            return vault

        # Resume if funding rate is positive and above resume threshold
        if vault.current_funding_rate > settings.vault_funding_rate_resume:
            signal = await get_cached_signal(vault.asset)
            if signal and signal.frss > FRSS_REDUCE_THRESHOLD:
                logger.info(
                    f"Resuming vault {vault.vault_id}: "
                    f"funding={vault.current_funding_rate}, FRSS={signal.frss}"
                )
                vault.vault_status = VaultStatus.ACTIVE
                await upsert_vault_state(vault)

        return vault
