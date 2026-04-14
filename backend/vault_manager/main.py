"""
Vault Manager — Service Entrypoint.

Persistent Python daemon that orchestrates all vault lifecycle operations:
- Position management on Pacifica
- NAV calculation and yield harvesting
- Signal-driven rebalancing via Elfa AI
- Health monitoring and circuit breakers
"""

import asyncio
import logging

from config import settings
from db.connection import close_connections
from db.queries import init_db, get_vault_state, upsert_vault_state
from models.vault import VaultState, VaultStatus
from pacifica.client import ZerovaExecutor
from pacifica.monitor import PositionMonitor
from signal_engine.elfa_client import ElfaSignalEngine
from signal_engine.scorer import SignalScorer
from vault_manager.position_manager import PositionManager
from vault_manager.rebalancer import Rebalancer
from vault_manager.health_monitor import HealthMonitor
from vault_manager.yield_harvester import record_funding_payment
from vault_manager.scheduler import create_scheduler, DEFAULT_VAULT_ID

from decimal import Decimal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("vault_manager")


async def ensure_vault_exists():
    """Create the default vault if it doesn't exist."""
    vault = await get_vault_state(DEFAULT_VAULT_ID)
    if vault is None:
        vault = VaultState(
            vault_id=DEFAULT_VAULT_ID,
            asset="BTC",
            vault_status=VaultStatus.ACTIVE,
        )
        await upsert_vault_state(vault)
        logger.info(f"Created default vault: {DEFAULT_VAULT_ID}")
    return vault


async def main():
    logger.info("Starting Zerova Vault Manager...")

    # Initialize database
    await init_db()
    await ensure_vault_exists()

    # Initialize services
    executor = ZerovaExecutor()
    if executor._dev_mode:
        logger.warning("Running in DEV MODE - no Pacifica private key configured")
    
    elfa = ElfaSignalEngine()
    scorer = SignalScorer(elfa)
    position_manager = PositionManager(executor)
    rebalancer = Rebalancer(position_manager, scorer)
    health_monitor = HealthMonitor()

    # Set up position monitor with callbacks
    async def on_funding(event: dict):
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault:
            amount = Decimal(str(event.get("data", {}).get("amount", "0")))
            received = event.get("data", {}).get("side") == "received"
            rate = float(event.get("data", {}).get("funding_rate", 0))
            tx_id = event.get("data", {}).get("tx_id", "")
            await record_funding_payment(vault, amount, received, rate, tx_id)

    async def on_margin_warning(event: dict):
        vault = await get_vault_state(DEFAULT_VAULT_ID)
        if vault:
            logger.warning(f"Margin warning: {event}")
            await position_manager.emergency_deleverage(vault)

    monitor = PositionMonitor(
        on_funding_payment=on_funding,
        on_margin_warning=on_margin_warning,
    )

    # Create and start scheduler
    scheduler = create_scheduler(rebalancer, health_monitor, scorer)
    scheduler.start()

    logger.info("Vault Manager started. Scheduler running.")

    # In dev mode, just keep the scheduler running without WebSocket
    if executor._dev_mode:
        logger.info("Dev mode: Scheduler running, WebSocket monitor disabled")
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            scheduler.shutdown()
            await executor.close()
            await elfa.close()
            await close_connections()
        return

    # Run WebSocket monitor alongside scheduler
    try:
        await monitor.subscribe("BTC")
        await monitor.connect()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        scheduler.shutdown()
        await monitor.stop()
        await executor.close()
        await elfa.close()
        await close_connections()


if __name__ == "__main__":
    asyncio.run(main())
