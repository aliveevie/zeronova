-- Zerova Protocol Database Schema

CREATE TABLE IF NOT EXISTS vault_state (
    vault_id            TEXT PRIMARY KEY,
    asset               TEXT NOT NULL,
    total_deposits_usdc NUMERIC(28, 8) DEFAULT 0,
    total_zv_usdc_supply NUMERIC(28, 8) DEFAULT 0,
    nav_per_share       NUMERIC(28, 8) DEFAULT 1.0,
    collateral_usdc_value NUMERIC(28, 8) DEFAULT 0,
    perp_notional       NUMERIC(28, 8) DEFAULT 0,
    perp_entry_price    NUMERIC(28, 8) DEFAULT 0,
    unrealised_perp_pnl NUMERIC(28, 8) DEFAULT 0,
    total_funding_received NUMERIC(28, 8) DEFAULT 0,
    total_funding_paid  NUMERIC(28, 8) DEFAULT 0,
    protocol_fees_accrued NUMERIC(28, 8) DEFAULT 0,
    net_delta           NUMERIC(28, 8) DEFAULT 0,
    margin_ratio        DOUBLE PRECISION DEFAULT 1.0,
    current_funding_rate DOUBLE PRECISION DEFAULT 0.0,
    vault_status        TEXT DEFAULT 'active',
    reserve_balance     NUMERIC(28, 8) DEFAULT 0,
    pending_withdrawals NUMERIC(28, 8) DEFAULT 0,
    last_rebalance_at   BIGINT DEFAULT 0,
    transition_epoch_count INT DEFAULT 0,
    updated_at          BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_positions (
    wallet_address      TEXT PRIMARY KEY,
    zv_usdc_balance     NUMERIC(28, 8) DEFAULT 0,
    usdc_deposited      NUMERIC(28, 8) DEFAULT 0,
    usdc_current_value  NUMERIC(28, 8) DEFAULT 0,
    unrealised_yield    NUMERIC(28, 8) DEFAULT 0,
    yield_pct           DOUBLE PRECISION DEFAULT 0.0,
    first_deposit_at    BIGINT DEFAULT 0,
    last_action_at      BIGINT DEFAULT 0,
    referral_code       TEXT,
    referral_earnings   NUMERIC(28, 8) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS deposit_events (
    event_id            TEXT PRIMARY KEY,
    wallet_address      TEXT NOT NULL,
    amount_usdc         NUMERIC(28, 8) NOT NULL,
    zv_usdc_minted      NUMERIC(28, 8) NOT NULL,
    nav_at_deposit      NUMERIC(28, 8) NOT NULL,
    source_chain        TEXT DEFAULT 'solana',
    referral_code       TEXT,
    tx_id               TEXT,
    timestamp           BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS withdrawal_events (
    event_id            TEXT PRIMARY KEY,
    wallet_address      TEXT NOT NULL,
    zv_usdc_burned      NUMERIC(28, 8) NOT NULL,
    usdc_returned       NUMERIC(28, 8) NOT NULL,
    nav_at_withdrawal   NUMERIC(28, 8) NOT NULL,
    tx_id               TEXT,
    timestamp           BIGINT NOT NULL,
    queue_position      INT DEFAULT 0,
    estimated_ready_at  BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS funding_events (
    event_id            TEXT PRIMARY KEY,
    vault_id            TEXT NOT NULL,
    asset               TEXT NOT NULL,
    amount_usdc         NUMERIC(28, 8) NOT NULL,
    direction           TEXT NOT NULL,
    funding_rate        DOUBLE PRECISION NOT NULL,
    position_size       NUMERIC(28, 8) NOT NULL,
    epoch_ts            BIGINT NOT NULL,
    pacifica_tx_id      TEXT
);

CREATE TABLE IF NOT EXISTS nav_history (
    id                  SERIAL PRIMARY KEY,
    vault_id            TEXT NOT NULL,
    nav_per_share       NUMERIC(28, 8) NOT NULL,
    total_assets        NUMERIC(28, 8) NOT NULL,
    timestamp           BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nav_history_vault_ts ON nav_history(vault_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_deposit_events_wallet ON deposit_events(wallet_address);
CREATE INDEX IF NOT EXISTS idx_withdrawal_events_wallet ON withdrawal_events(wallet_address);
CREATE INDEX IF NOT EXISTS idx_funding_events_vault ON funding_events(vault_id, epoch_ts);
