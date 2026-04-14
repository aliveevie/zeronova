from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import time
import uuid


class EventType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FUNDING_RECEIVED = "funding_received"
    FUNDING_PAID = "funding_paid"
    REBALANCE = "rebalance"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class FundingEvent:
    vault_id: str
    asset: str
    amount_usdc: Decimal
    direction: str  # "received" | "paid"
    funding_rate: float
    position_size: Decimal
    epoch_ts: int
    pacifica_tx_id: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class DepositEvent:
    wallet_address: str
    amount_usdc: Decimal
    zv_usdc_minted: Decimal
    nav_at_deposit: Decimal
    source_chain: str = "solana"
    referral_code: str | None = None
    tx_id: str = ""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class WithdrawalEvent:
    wallet_address: str
    zv_usdc_burned: Decimal
    usdc_returned: Decimal
    nav_at_withdrawal: Decimal
    tx_id: str = ""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    queue_position: int = 0
    estimated_ready_at: int = 0
