"""
Elfa AI Signal Client.

Queries Elfa AI v2 API to produce sentiment signals for vault assets.
Uses top-mentions, trending tokens, and keyword mentions to derive a
composite Funding Rate Sentiment Score (FRSS) used for rebalancing.

Elfa API docs: https://docs.elfa.ai
Auth: x-elfa-api-key header
"""

import logging
from dataclasses import dataclass

import httpx

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class SignalScore:
    asset: str
    frss: float  # 0.0 (max bearish) to 1.0 (max bullish)
    funding_rate_estimate: float
    social_volume_24h: int
    sentiment_trend: str  # "improving" | "stable" | "deteriorating"
    confidence: float  # 0.0 to 1.0
    updated_at: int  # epoch ms


class ElfaSignalEngine:
    BASE_URL = "https://docs.elfa.ai"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.elfa_api_key
        self.client = httpx.AsyncClient(
            headers={"x-elfa-api-key": self.api_key},
            timeout=30.0,
        )

    async def get_top_mentions(self, ticker: str, time_window: str = "24h") -> dict:
        """Fetch top social mentions for a given asset ticker."""
        resp = await self.client.get(
            f"{self.BASE_URL}/v2/data/top-mentions",
            params={"ticker": ticker, "timeWindow": time_window},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_trending_tokens(self, time_window: str = "24h") -> dict:
        """Fetch currently trending tokens by social volume."""
        resp = await self.client.get(
            f"{self.BASE_URL}/v2/aggregations/trending-tokens",
            params={"timeWindow": time_window},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_keyword_mentions(
        self, keywords: str, time_window: str = "24h", limit: int = 50
    ) -> dict:
        """Search mentions by keywords (e.g., 'BTC funding rate')."""
        resp = await self.client.get(
            f"{self.BASE_URL}/v2/data/keyword-mentions",
            params={
                "keywords": keywords,
                "timeWindow": time_window,
                "limit": limit,
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def get_event_summary(self, keywords: str, time_window: str = "24h") -> dict:
        """Get AI-generated event summary from keyword mentions."""
        resp = await self.client.get(
            f"{self.BASE_URL}/v2/data/event-summary",
            params={"keywords": keywords, "timeWindow": time_window},
        )
        resp.raise_for_status()
        return resp.json()

    async def chat(self, message: str) -> dict:
        """Use Elfa AI chat for direct sentiment analysis."""
        resp = await self.client.post(
            f"{self.BASE_URL}/v2/chat",
            json={"message": message, "speed": "fast"},
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self.client.aclose()
