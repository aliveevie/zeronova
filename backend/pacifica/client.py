"""
ZerovaExecutor — Pacifica order execution client.

Wraps the Pacifica REST API to provide vault-specific order management.
All orders embed the ZEROVA01 builder code for fee attribution.
Uses the exact signing pattern from the official Pacifica Python SDK.
"""

import time
import uuid
from decimal import Decimal

import httpx
from solders.keypair import Keypair

from config import settings
from pacifica.signing import sign_message
from pacifica.builder import ZEROVA_BUILDER_CODE


class ZerovaExecutor:
    def __init__(self, private_key: str | None = None):
        key = private_key or settings.pacifica_private_key
        if key:
            self.keypair = Keypair.from_base58_string(key)
            self.public_key = str(self.keypair.pubkey())
        else:
            self.keypair = None
            self.public_key = "DEV_MODE_NO_KEY"
        self.api_url = settings.pacifica_api_url
        self.builder_code = ZEROVA_BUILDER_CODE
        self._client = httpx.AsyncClient(timeout=30.0)
        self._dev_mode = self.keypair is None

    async def _send_signed_request(
        self,
        endpoint: str,
        msg_type: str,
        payload: dict,
    ) -> dict:
        """Build, sign, and send a request to Pacifica REST API."""
        if self._dev_mode:
            return {"status": "dev_mode", "order_id": f"dev_{uuid.uuid4()}"}

        timestamp = int(time.time() * 1000)

        header = {
            "type": msg_type,
            "timestamp": timestamp,
            "expiry_window": 5000,
        }

        _, signature = sign_message(header, payload, self.keypair)

        request_body = {
            "account": self.public_key,
            "signature": signature,
            "timestamp": timestamp,
            "expiry_window": 5000,
            **payload,
            "builder_code": self.builder_code,
        }

        resp = await self._client.post(
            f"{self.api_url}{endpoint}",
            json=request_body,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    async def open_short_position(
        self,
        symbol: str,
        notional_usdc: Decimal,
        slippage_pct: float = 0.3,
    ) -> dict:
        """
        Open a market short perpetual position on Pacifica.
        Builder code is embedded for fee attribution.
        """
        payload = {
            "symbol": symbol,
            "reduce_only": False,
            "amount": str(notional_usdc),
            "side": "ask",  # short = ask side
            "slippage_percent": str(slippage_pct),
            "client_order_id": str(uuid.uuid4()),
        }
        return await self._send_signed_request(
            "/orders/create_market", "create_market_order", payload
        )

    async def close_short_position(
        self,
        symbol: str,
        amount: Decimal,
        slippage_pct: float = 0.5,
    ) -> dict:
        """Close an existing short position (reduce only)."""
        payload = {
            "symbol": symbol,
            "reduce_only": True,
            "amount": str(amount),
            "side": "bid",  # close short = buy back = bid
            "slippage_percent": str(slippage_pct),
            "client_order_id": str(uuid.uuid4()),
        }
        return await self._send_signed_request(
            "/orders/create_market", "create_market_order", payload
        )

    async def create_limit_order(
        self,
        symbol: str,
        price: Decimal,
        amount: Decimal,
        side: str,
        reduce_only: bool = False,
        tif: str = "GTC",
    ) -> dict:
        """Place a limit order on the Pacifica orderbook."""
        payload = {
            "symbol": symbol,
            "price": str(price),
            "reduce_only": reduce_only,
            "amount": str(amount),
            "side": side,
            "tif": tif,
            "client_order_id": str(uuid.uuid4()),
        }
        return await self._send_signed_request(
            "/orders/create", "create_order", payload
        )

    async def set_position_tpsl(
        self,
        symbol: str,
        side: str,
        tp_price: Decimal | None = None,
        sl_price: Decimal | None = None,
    ) -> dict:
        """Set take-profit and/or stop-loss for an open position."""
        payload: dict = {"symbol": symbol, "side": side}

        if tp_price is not None:
            payload["take_profit"] = {
                "stop_price": str(tp_price),
                "client_order_id": str(uuid.uuid4()),
            }
        if sl_price is not None:
            payload["stop_loss"] = {
                "stop_price": str(sl_price),
                "client_order_id": str(uuid.uuid4()),
            }

        return await self._send_signed_request(
            "/positions/tpsl", "set_position_tpsl", payload
        )

    async def get_trade_history(self, symbol: str | None = None) -> dict:
        """Fetch trade history for the vault account."""
        params = {"account": self.public_key, "builder_code": self.builder_code}
        if symbol:
            params["symbol"] = symbol

        resp = await self._client.get(
            f"{self.api_url}/trades/history", params=params
        )
        resp.raise_for_status()
        return resp.json()

    async def get_builder_trades(self) -> dict:
        """Fetch all trades attributed to the ZEROVA builder code."""
        resp = await self._client.get(
            f"{self.api_url}/builder/trades",
            params={"builder_code": self.builder_code},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_positions(self) -> list[dict]:
        """Fetch all open positions for the vault account."""
        if self._dev_mode:
            return []
        resp = await self._client.get(
            f"{self.api_url}/positions",
            params={"account": self.public_key},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", []) if data.get("success") else []

    async def get_open_orders(self) -> list[dict]:
        """Fetch all open orders for the vault account."""
        if self._dev_mode:
            return []
        resp = await self._client.get(
            f"{self.api_url}/orders",
            params={"account": self.public_key},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", []) if data.get("success") else []

    async def get_funding_rate(self, symbol: str) -> float:
        """Fetch current funding rate for a symbol."""
        if self._dev_mode:
            return 0.0001
        resp = await self._client.get(
            f"{self.api_url}/funding_rate/{symbol}",
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                return float(data["data"].get("funding_rate", 0))
        return 0.0

    async def close(self):
        await self._client.aclose()
