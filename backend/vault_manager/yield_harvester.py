"""
Yield Harvester.

Tracks and accounts for funding rate payments received from Pacifica
short perpetual positions. Updates vault accounting on each funding event.
"""

import logging
import time
from decimal import Decimal

from models.vault import VaultState
from models.events import FundingEvent
from db.queries import upsert_vault_state, insert_funding_event
from config import settings

logger = logging.getLogger(__name__)

# Protocol fee: taken as a percentage of yield
PROTOCOL_FEE_BPS = settings.vault_protocol_fee_bps  # 50 = 0.50%


async def record_funding_payment(
    vault: VaultState,
    amount_usdc: Decimal,
    received: bool,
    funding_rate: float,
    pacifica_tx_id: str = "",
) -> VaultState:
    """
    Record a funding rate payment event and update vault accounting.

    Args:
        vault: Current vault state
        amount_usdc: Absolute amount of the funding payment
        received: True if vault (short) received the payment
        funding_rate: The 8h funding rate at time of payment
        pacifica_tx_id: Transaction ID from Pacifica
    """
    now = int(time.time() * 1000)

    if received:
        # Calculate and deduct protocol fee from received funding
        protocol_fee = amount_usdc * Decimal(PROTOCOL_FEE_BPS) / Decimal("10000")
        net_amount = amount_usdc - protocol_fee

        vault.total_funding_received += net_amount
        vault.protocol_fees_accrued += protocol_fee
        direction = "received"

        logger.info(
            f"Funding received: {amount_usdc} USDC "
            f"(net: {net_amount}, fee: {protocol_fee})"
        )
    else:
        vault.total_funding_paid += amount_usdc
        direction = "paid"

        logger.warning(f"Funding paid: {amount_usdc} USDC (shorts paying longs)")

    vault.current_funding_rate = funding_rate
    vault.updated_at = now

    # Persist funding event
    event = FundingEvent(
        vault_id=vault.vault_id,
        asset=vault.asset,
        amount_usdc=amount_usdc,
        direction=direction,
        funding_rate=funding_rate,
        position_size=vault.perp_notional,
        epoch_ts=now,
        pacifica_tx_id=pacifica_tx_id,
    )
    await insert_funding_event(event)
    await upsert_vault_state(vault)

    return vault
