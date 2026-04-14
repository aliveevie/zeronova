from decimal import Decimal
from db.connection import get_db_pool
from models.vault import VaultState, VaultStatus
from models.user import UserPosition
from models.events import DepositEvent, WithdrawalEvent, FundingEvent
import time


async def init_db():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        with open("db/migrations/001_initial.sql") as f:
            await conn.execute(f.read())


# --- Vault State ---

async def get_vault_state(vault_id: str) -> VaultState | None:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM vault_state WHERE vault_id = $1", vault_id
        )
        if not row:
            return None
        return VaultState(
            vault_id=row["vault_id"],
            asset=row["asset"],
            total_deposits_usdc=row["total_deposits_usdc"],
            total_zv_usdc_supply=row["total_zv_usdc_supply"],
            nav_per_share=row["nav_per_share"],
            collateral_usdc_value=row["collateral_usdc_value"],
            perp_notional=row["perp_notional"],
            perp_entry_price=row["perp_entry_price"],
            unrealised_perp_pnl=row["unrealised_perp_pnl"],
            total_funding_received=row["total_funding_received"],
            total_funding_paid=row["total_funding_paid"],
            protocol_fees_accrued=row["protocol_fees_accrued"],
            net_delta=row["net_delta"],
            margin_ratio=row["margin_ratio"],
            current_funding_rate=row["current_funding_rate"],
            vault_status=VaultStatus(row["vault_status"]),
            reserve_balance=row["reserve_balance"],
            pending_withdrawals=row["pending_withdrawals"],
            last_rebalance_at=row["last_rebalance_at"],
            transition_epoch_count=row["transition_epoch_count"],
            updated_at=row["updated_at"],
        )


async def upsert_vault_state(vault: VaultState):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO vault_state (
                vault_id, asset, total_deposits_usdc, total_zv_usdc_supply,
                nav_per_share, collateral_usdc_value, perp_notional, perp_entry_price,
                unrealised_perp_pnl, total_funding_received, total_funding_paid,
                protocol_fees_accrued, net_delta, margin_ratio, current_funding_rate,
                vault_status, reserve_balance, pending_withdrawals,
                last_rebalance_at, transition_epoch_count, updated_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21)
            ON CONFLICT (vault_id) DO UPDATE SET
                total_deposits_usdc = EXCLUDED.total_deposits_usdc,
                total_zv_usdc_supply = EXCLUDED.total_zv_usdc_supply,
                nav_per_share = EXCLUDED.nav_per_share,
                collateral_usdc_value = EXCLUDED.collateral_usdc_value,
                perp_notional = EXCLUDED.perp_notional,
                perp_entry_price = EXCLUDED.perp_entry_price,
                unrealised_perp_pnl = EXCLUDED.unrealised_perp_pnl,
                total_funding_received = EXCLUDED.total_funding_received,
                total_funding_paid = EXCLUDED.total_funding_paid,
                protocol_fees_accrued = EXCLUDED.protocol_fees_accrued,
                net_delta = EXCLUDED.net_delta,
                margin_ratio = EXCLUDED.margin_ratio,
                current_funding_rate = EXCLUDED.current_funding_rate,
                vault_status = EXCLUDED.vault_status,
                reserve_balance = EXCLUDED.reserve_balance,
                pending_withdrawals = EXCLUDED.pending_withdrawals,
                last_rebalance_at = EXCLUDED.last_rebalance_at,
                transition_epoch_count = EXCLUDED.transition_epoch_count,
                updated_at = EXCLUDED.updated_at
            """,
            vault.vault_id, vault.asset,
            vault.total_deposits_usdc, vault.total_zv_usdc_supply,
            vault.nav_per_share, vault.collateral_usdc_value,
            vault.perp_notional, vault.perp_entry_price,
            vault.unrealised_perp_pnl, vault.total_funding_received,
            vault.total_funding_paid, vault.protocol_fees_accrued,
            vault.net_delta, vault.margin_ratio, vault.current_funding_rate,
            vault.vault_status.value, vault.reserve_balance,
            vault.pending_withdrawals, vault.last_rebalance_at,
            vault.transition_epoch_count, vault.updated_at,
        )


# --- User Positions ---

async def get_user_position(wallet: str) -> UserPosition | None:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM user_positions WHERE wallet_address = $1", wallet
        )
        if not row:
            return None
        return UserPosition(
            wallet_address=row["wallet_address"],
            zv_usdc_balance=row["zv_usdc_balance"],
            usdc_deposited=row["usdc_deposited"],
            usdc_current_value=row["usdc_current_value"],
            unrealised_yield=row["unrealised_yield"],
            yield_pct=row["yield_pct"],
            first_deposit_at=row["first_deposit_at"],
            last_action_at=row["last_action_at"],
            referral_code=row["referral_code"],
            referral_earnings=row["referral_earnings"],
        )


async def upsert_user_position(pos: UserPosition):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_positions (
                wallet_address, zv_usdc_balance, usdc_deposited,
                usdc_current_value, unrealised_yield, yield_pct,
                first_deposit_at, last_action_at, referral_code, referral_earnings
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
            ON CONFLICT (wallet_address) DO UPDATE SET
                zv_usdc_balance = EXCLUDED.zv_usdc_balance,
                usdc_deposited = EXCLUDED.usdc_deposited,
                usdc_current_value = EXCLUDED.usdc_current_value,
                unrealised_yield = EXCLUDED.unrealised_yield,
                yield_pct = EXCLUDED.yield_pct,
                last_action_at = EXCLUDED.last_action_at,
                referral_code = EXCLUDED.referral_code,
                referral_earnings = EXCLUDED.referral_earnings
            """,
            pos.wallet_address, pos.zv_usdc_balance, pos.usdc_deposited,
            pos.usdc_current_value, pos.unrealised_yield, pos.yield_pct,
            pos.first_deposit_at, pos.last_action_at,
            pos.referral_code, pos.referral_earnings,
        )


# --- Events ---

async def insert_deposit_event(event: DepositEvent):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO deposit_events
            (event_id, wallet_address, amount_usdc, zv_usdc_minted,
             nav_at_deposit, source_chain, referral_code, tx_id, timestamp)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            """,
            event.event_id, event.wallet_address, event.amount_usdc,
            event.zv_usdc_minted, event.nav_at_deposit, event.source_chain,
            event.referral_code, event.tx_id, event.timestamp,
        )


async def insert_withdrawal_event(event: WithdrawalEvent):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO withdrawal_events
            (event_id, wallet_address, zv_usdc_burned, usdc_returned,
             nav_at_withdrawal, tx_id, timestamp, queue_position, estimated_ready_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            """,
            event.event_id, event.wallet_address, event.zv_usdc_burned,
            event.usdc_returned, event.nav_at_withdrawal, event.tx_id,
            event.timestamp, event.queue_position, event.estimated_ready_at,
        )


async def insert_funding_event(event: FundingEvent):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO funding_events
            (event_id, vault_id, asset, amount_usdc, direction,
             funding_rate, position_size, epoch_ts, pacifica_tx_id)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            """,
            event.event_id, event.vault_id, event.asset,
            event.amount_usdc, event.direction, event.funding_rate,
            event.position_size, event.epoch_ts, event.pacifica_tx_id,
        )


async def insert_nav_snapshot(vault_id: str, nav: Decimal, total_assets: Decimal):
    pool = await get_db_pool()
    ts = int(time.time() * 1000)
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO nav_history (vault_id, nav_per_share, total_assets, timestamp) VALUES ($1,$2,$3,$4)",
            vault_id, nav, total_assets, ts,
        )


async def get_nav_history(vault_id: str, since_ts: int) -> list[dict]:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT nav_per_share, total_assets, timestamp FROM nav_history WHERE vault_id = $1 AND timestamp >= $2 ORDER BY timestamp",
            vault_id, since_ts,
        )
        return [dict(r) for r in rows]


async def get_user_deposit_history(wallet: str) -> list[dict]:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM deposit_events WHERE wallet_address = $1 ORDER BY timestamp DESC",
            wallet,
        )
        return [dict(r) for r in rows]


async def get_user_withdrawal_history(wallet: str) -> list[dict]:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM withdrawal_events WHERE wallet_address = $1 ORDER BY timestamp DESC",
            wallet,
        )
        return [dict(r) for r in rows]
