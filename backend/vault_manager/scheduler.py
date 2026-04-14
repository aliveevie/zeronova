"""
Vault Manager Scheduler.

Configures APScheduler jobs for periodic vault operations:
- Position sync (1 min)
- NAV recalculation (5 min)
- Rebalance evaluation (1 hour)
- Signal refresh from Elfa AI (30 min)
- Withdrawal processing (15 min)
- Health monitoring (2 min)
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from models.vault import VaultState
from vault_manager.nav_engine import recalculate as nav_recalculate
from vault_manager.position_sync import sync_positions
from vault_manager.rebalancer import Rebalancer
from vault_manager.health_monitor import HealthMonitor
from signal_engine.scorer import SignalScorer
from signal_engine.elfa_client import ElfaSignalEngine
from signal_engine.cache import cache_signal
from db.queries import get_vault_state
from pacifica.client import ZerovaExecutor

logger = logging.getLogger(__name__)

DEFAULT_VAULT_ID = "zerova-btc-v1"

_executor: ZerovaExecutor | None = None


def create_scheduler(
    rebalancer: Rebalancer,
    health_monitor: HealthMonitor,
    signal_scorer: SignalScorer,
) -> AsyncIOScheduler:
    """Create and configure the vault manager scheduler."""
    global _executor
    _executor = ZerovaExecutor()
    
    scheduler = AsyncIOScheduler()

    async def _position_sync_job():
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault and _executor:
            await sync_positions(vault, _executor)

    async def _nav_job():
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault:
            await nav_recalculate(vault)

    async def _rebalance_job():
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault:
            await rebalancer.evaluate(vault)
            await rebalancer.check_resume(vault)

    async def _signal_job():
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault:
            try:
                score = await signal_scorer.compute_frss(vault.asset)
                await cache_signal(score)
                logger.info(f"Signal refreshed: {vault.asset} FRSS={score.frss}")
            except Exception as e:
                logger.error(f"Signal refresh failed: {e}")

    async def _health_job():
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault:
            report = await health_monitor.check(vault)
            if report.get("circuit_breaker_triggered"):
                logger.critical(f"Health check: circuit breaker triggered!")

    # Register jobs
    scheduler.add_job(_position_sync_job, "interval", minutes=1, id="position_sync")
    scheduler.add_job(_nav_job, "interval", minutes=5, id="nav_recalculate")
    scheduler.add_job(_rebalance_job, "interval", hours=1, id="rebalance_evaluate")
    scheduler.add_job(_signal_job, "interval", minutes=30, id="signal_refresh")
    scheduler.add_job(_health_job, "interval", minutes=2, id="health_check")

    return scheduler
