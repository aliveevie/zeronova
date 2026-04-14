"""
Pacifica WebSocket Position Monitor.

Maintains a persistent WebSocket connection to track:
- Real-time position P&L
- Funding rate payments received/paid
- Liquidation proximity alerts
- Order fill confirmations
"""

import asyncio
import json
import logging
import uuid
import time

import websockets
from decimal import Decimal
from solders.keypair import Keypair

from config import settings
from pacifica.signing import sign_message

logger = logging.getLogger(__name__)


class PositionMonitor:
    def __init__(
        self,
        on_funding_payment=None,
        on_margin_warning=None,
        on_position_update=None,
        on_order_fill=None,
    ):
        self.ws_url = settings.pacifica_ws_url
        key = settings.pacifica_private_key
        if key:
            self.keypair = Keypair.from_base58_string(key)
            self.public_key = str(self.keypair.pubkey())
            self._dev_mode = False
        else:
            self.keypair = None
            self.public_key = "DEV_MODE_NO_KEY"
            self._dev_mode = True
        self._ws = None
        self._running = False
        self._subscriptions: set[str] = set()

        # Callbacks
        self.on_funding_payment = on_funding_payment
        self.on_margin_warning = on_margin_warning
        self.on_position_update = on_position_update
        self.on_order_fill = on_order_fill

    async def connect(self):
        """Establish WebSocket connection with auto-reconnect."""
        if self._dev_mode:
            logger.info("Dev mode: WebSocket monitor disabled")
            return

        self._running = True
        while self._running:
            try:
                async with websockets.connect(
                    self.ws_url, ping_interval=30
                ) as ws:
                    self._ws = ws
                    logger.info("Connected to Pacifica WebSocket")

                    # Re-subscribe on reconnect
                    for symbol in self._subscriptions:
                        await self._subscribe_prices(ws, symbol)

                    await self._listen(ws)
            except websockets.ConnectionClosed:
                logger.warning("WebSocket disconnected, reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket error: {e}, reconnecting in 10s...")
                await asyncio.sleep(10)

    async def _listen(self, ws):
        """Process incoming WebSocket messages."""
        async for raw in ws:
            try:
                msg = json.loads(raw)
                await self._dispatch(msg)
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON message: {raw[:100]}")

    async def _dispatch(self, msg: dict):
        """Route incoming messages to appropriate handlers."""
        msg_type = msg.get("type") or msg.get("channel", "")

        if "funding" in msg_type and self.on_funding_payment:
            await self.on_funding_payment(msg)

        elif "margin" in msg_type and self.on_margin_warning:
            margin = msg.get("data", {}).get("margin_ratio")
            if margin is not None and float(margin) < settings.vault_margin_emergency_floor:
                await self.on_margin_warning(msg)

        elif "position" in msg_type and self.on_position_update:
            await self.on_position_update(msg)

        elif "fill" in msg_type and self.on_order_fill:
            await self.on_order_fill(msg)

    async def subscribe(self, symbol: str):
        """Subscribe to price and position updates for a symbol."""
        self._subscriptions.add(symbol)
        if self._ws:
            await self._subscribe_prices(self._ws, symbol)

    async def _subscribe_prices(self, ws, symbol: str):
        """Send subscription message for a symbol."""
        msg = {
            "id": str(uuid.uuid4()),
            "params": {
                "subscribe_prices": {
                    "symbol": symbol,
                    "account": self.public_key,
                }
            },
        }
        await ws.send(json.dumps(msg))

    async def send_market_order(
        self, symbol: str, side: str, amount: str, slippage: str = "0.5"
    ) -> dict:
        """Send a market order via WebSocket for lower latency."""
        if not self._ws:
            raise RuntimeError("WebSocket not connected")

        timestamp = int(time.time() * 1000)
        header = {
            "type": "create_market_order",
            "timestamp": timestamp,
            "expiry_window": 5000,
        }
        payload = {
            "symbol": symbol,
            "reduce_only": False,
            "amount": amount,
            "side": side,
            "slippage_percent": slippage,
            "client_order_id": str(uuid.uuid4()),
        }

        _, signature = sign_message(header, payload, self.keypair)

        ws_msg = {
            "id": str(uuid.uuid4()),
            "params": {
                "create_market_order": {
                    "account": self.public_key,
                    "signature": signature,
                    "timestamp": timestamp,
                    "expiry_window": 5000,
                    **payload,
                    "builder_code": settings.pacifica_builder_code,
                }
            },
        }

        await self._ws.send(json.dumps(ws_msg))
        response = await self._ws.recv()
        return json.loads(response)

    async def stop(self):
        """Gracefully stop the monitor."""
        self._running = False
        if self._ws:
            await self._ws.close()
