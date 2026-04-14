"""
Signal Cache.

Caches Elfa AI signal scores in Redis to avoid redundant API calls.
Signals are cached per asset with a configurable TTL (default: 15 min).
"""

import json
import logging
from signal_engine.elfa_client import SignalScore
from db.connection import get_redis

logger = logging.getLogger(__name__)

SIGNAL_CACHE_TTL = 900  # 15 minutes
SIGNAL_KEY_PREFIX = "zerova:signal:"


async def get_cached_signal(asset: str) -> SignalScore | None:
    """Retrieve a cached signal score for an asset."""
    redis = await get_redis()
    raw = await redis.get(f"{SIGNAL_KEY_PREFIX}{asset}")
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return SignalScore(**data)
    except Exception as e:
        logger.warning(f"Failed to deserialize cached signal for {asset}: {e}")
        return None


async def cache_signal(score: SignalScore):
    """Cache a signal score for an asset."""
    redis = await get_redis()
    data = {
        "asset": score.asset,
        "frss": score.frss,
        "funding_rate_estimate": score.funding_rate_estimate,
        "social_volume_24h": score.social_volume_24h,
        "sentiment_trend": score.sentiment_trend,
        "confidence": score.confidence,
        "updated_at": score.updated_at,
    }
    await redis.set(
        f"{SIGNAL_KEY_PREFIX}{score.asset}",
        json.dumps(data),
        ex=SIGNAL_CACHE_TTL,
    )


async def invalidate_signal(asset: str):
    """Remove a cached signal for an asset."""
    redis = await get_redis()
    await redis.delete(f"{SIGNAL_KEY_PREFIX}{asset}")
