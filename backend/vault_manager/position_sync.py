"""
Position Sync.

Fetches positions from Pacifica and updates the vault state accordingly.
"""

import logging
from decimal import Decimal

from pacifica.client import ZerovaExecutor
from models.vault import VaultState
from db.queries import upsert_vault_state

logger = logging.getLogger(__name__)


async def sync_positions(vault: VaultState, executor: ZerovaExecutor) -> VaultState:
    """
    Sync vault state with actual Pacifica positions.
    Updates perp_notional, entry_price, unrealised_pnl, and funding rate.
    """
    try:
        positions = await executor.get_positions()
        funding_rate = await executor.get_funding_rate(vault.asset)
        
        vault.current_funding_rate = funding_rate
        
        btc_position = next(
            (p for p in positions if p.get("symbol") == vault.asset),
            None
        )
        
        if btc_position:
            amount = Decimal(btc_position.get("amount", "0"))
            entry_price = Decimal(btc_position.get("entry_price", "0"))
            side = btc_position.get("side", "")
            
            notional = amount * entry_price
            vault.perp_notional = notional
            vault.perp_entry_price = entry_price
            
            if side == "ask":
                vault.net_delta = -amount
            else:
                vault.net_delta = amount
            
            logger.info(
                f"Position synced: {vault.asset} {side} {amount} @ {entry_price} "
                f"(notional=${notional:.2f})"
            )
        else:
            vault.perp_notional = Decimal("0")
            vault.perp_entry_price = Decimal("0")
            vault.net_delta = Decimal("0")
            logger.info(f"No {vault.asset} position found")
        
        await upsert_vault_state(vault)
        return vault
        
    except Exception as e:
        logger.error(f"Failed to sync positions: {e}")
        return vault
