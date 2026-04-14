from dataclasses import dataclass, field
from decimal import Decimal
import time


@dataclass
class UserPosition:
    wallet_address: str
    zv_usdc_balance: Decimal = Decimal("0")
    usdc_deposited: Decimal = Decimal("0")
    usdc_current_value: Decimal = Decimal("0")
    unrealised_yield: Decimal = Decimal("0")
    yield_pct: float = 0.0
    first_deposit_at: int = 0
    last_action_at: int = field(default_factory=lambda: int(time.time() * 1000))
    referral_code: str | None = None
    referral_earnings: Decimal = Decimal("0")
