"""
Health Monitor & Circuit Breakers.

Monitors vault health metrics and triggers hard stops when critical
conditions are met. Circuit breakers immediately pause vault operations
and move to PARKED state.
"""

import logging
import time
from typing import Callable

from models.vault import VaultState, VaultStatus
from db.queries import upsert_vault_state
from config import settings

logger = logging.getLogger(__name__)


class VaultCircuitBreaker:
    """
    Hard stops that pause vault operations.
    Triggered conditions immediately move vault to PARKED state.
    """

    TRIGGERS: dict[str, Callable[[VaultState], bool]] = {
        "margin_critical": lambda s: s.margin_ratio < settings.vault_margin_emergency_floor,
        "nav_drawdown": lambda s: s.nav_drawdown_7d > 0.05,
        "api_failure_streak": lambda s: s.consecutive_api_failures > 5,
        "funding_extreme": lambda s: abs(s.current_funding_rate) > 0.01,
    }

    async def evaluate(self, state: VaultState) -> bool:
        """Check all circuit breaker conditions. Returns True if any triggered."""
        for name, condition in self.TRIGGERS.items():
            if condition(state):
                await self._trigger_pause(name, state)
                return True
        return False

    async def _trigger_pause(self, trigger_name: str, state: VaultState):
        """Pause the vault and log the circuit breaker trigger."""
        logger.critical(
            f"CIRCUIT BREAKER: {trigger_name} triggered for vault {state.vault_id}. "
            f"margin_ratio={state.margin_ratio}, "
            f"funding_rate={state.current_funding_rate}, "
            f"nav_drawdown_7d={state.nav_drawdown_7d}"
        )
        state.vault_status = VaultStatus.PARKED
        state.updated_at = int(time.time() * 1000)
        await upsert_vault_state(state)


class HealthMonitor:
    def __init__(self):
        self.circuit_breaker = VaultCircuitBreaker()
        self._last_check: dict[str, int] = {}

    async def check(self, vault: VaultState) -> dict:
        """
        Run health check and return status report.
        """
        now = int(time.time() * 1000)
        report = {
            "vault_id": vault.vault_id,
            "status": vault.vault_status.value,
            "margin_ratio": vault.margin_ratio,
            "funding_rate": vault.current_funding_rate,
            "net_delta": str(vault.net_delta),
            "nav_drawdown_7d": vault.nav_drawdown_7d,
            "consecutive_api_failures": vault.consecutive_api_failures,
            "checked_at": now,
            "circuit_breaker_triggered": False,
        }

        # Run circuit breakers
        triggered = await self.circuit_breaker.evaluate(vault)
        report["circuit_breaker_triggered"] = triggered

        if triggered:
            report["status"] = VaultStatus.PARKED.value

        # Margin health classification
        if vault.margin_ratio >= settings.vault_margin_safe_floor:
            report["margin_health"] = "healthy"
        elif vault.margin_ratio >= settings.vault_margin_emergency_floor:
            report["margin_health"] = "warning"
        else:
            report["margin_health"] = "critical"

        self._last_check[vault.vault_id] = now
        return report
