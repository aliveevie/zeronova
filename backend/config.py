from pydantic_settings import BaseSettings
from decimal import Decimal


class Settings(BaseSettings):
    # Pacifica
    pacifica_api_url: str = "https://api.pacifica.fi/api/v1"
    pacifica_ws_url: str = "wss://ws.pacifica.fi/ws"
    pacifica_private_key: str = ""
    pacifica_builder_code: str = "ZEROVA01"

    # Elfa AI
    elfa_api_key: str = ""
    elfa_api_url: str = "https://docs.elfa.ai"

    # Rhinofi
    rhinofi_api_key: str = ""

    # Database
    database_url: str = "postgresql://zerova:password@localhost:5432/zerova"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Vault Parameters
    vault_delta_drift_threshold: float = 0.05
    vault_margin_safe_floor: float = 0.30
    vault_margin_emergency_floor: float = 0.15
    vault_funding_rate_floor: float = -0.0001
    vault_funding_rate_resume: float = 0.0001
    vault_min_hold_epochs: int = 3
    vault_protocol_fee_bps: int = 50
    vault_builder_fee_rate: float = 0.0005

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
