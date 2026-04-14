from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import time


class VaultStatus(str, Enum):
    ACTIVE = "active"
    TRANSITIONING = "transitioning"
    PARKED = "parked"


class RebalanceTrigger(str, Enum):
    DELTA_DRIFT = "delta_drift"
    FUNDING_FLIP = "funding_flip"
    MARGIN_THRESHOLD = "margin_threshold"
    SENTIMENT_EXIT = "sentiment_exit"
    WITHDRAWAL_QUEUE = "withdrawal_queue"


@dataclass
class VaultState:
    vault_id: str
    asset: str
    total_deposits_usdc: Decimal = Decimal("0")
    total_zv_usdc_supply: Decimal = Decimal("0")
    nav_per_share: Decimal = Decimal("1.0")
    collateral_usdc_value: Decimal = Decimal("0")
    perp_notional: Decimal = Decimal("0")
    perp_entry_price: Decimal = Decimal("0")
    unrealised_perp_pnl: Decimal = Decimal("0")
    total_funding_received: Decimal = Decimal("0")
    total_funding_paid: Decimal = Decimal("0")
    protocol_fees_accrued: Decimal = Decimal("0")
    net_delta: Decimal = Decimal("0")
    margin_ratio: float = 1.0
    current_funding_rate: float = 0.0
    vault_status: VaultStatus = VaultStatus.ACTIVE
    reserve_balance: Decimal = Decimal("0")
    pending_withdrawals: Decimal = Decimal("0")
    last_rebalance_at: int = 0
    transition_epoch_count: int = 0
    nav_7d_ago: Decimal = Decimal("1.0")
    nav_drawdown_7d: float = 0.0
    consecutive_api_failures: int = 0
    updated_at: int = field(default_factory=lambda: int(time.time() * 1000))
