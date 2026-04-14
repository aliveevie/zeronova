"""
Signal API Routes.

Exposes Elfa AI sentiment signals to the frontend.
"""

from fastapi import APIRouter, HTTPException

from signal_engine.elfa_client import ElfaSignalEngine
from signal_engine.scorer import SignalScorer
from signal_engine.cache import get_cached_signal, cache_signal

router = APIRouter(prefix="/api/v1/signal", tags=["signal"])


@router.get("/{asset}")
async def get_signal(asset: str):
    """
    Returns the SignalScore (FRSS, trend, confidence, estimated funding rate)
    for a given asset. Uses cache when available.
    """
    asset = asset.upper()

    # Try cache first
    cached = await get_cached_signal(asset)
    if cached:
        return {
            "asset": cached.asset,
            "frss": cached.frss,
            "funding_rate_estimate": cached.funding_rate_estimate,
            "social_volume_24h": cached.social_volume_24h,
            "sentiment_trend": cached.sentiment_trend,
            "confidence": cached.confidence,
            "updated_at": cached.updated_at,
            "cached": True,
        }

    # Compute fresh signal
    try:
        elfa = ElfaSignalEngine()
        scorer = SignalScorer(elfa)
        score = await scorer.compute_frss(asset)
        await cache_signal(score)
        await elfa.close()

        return {
            "asset": score.asset,
            "frss": score.frss,
            "funding_rate_estimate": score.funding_rate_estimate,
            "social_volume_24h": score.social_volume_24h,
            "sentiment_trend": score.sentiment_trend,
            "confidence": score.confidence,
            "updated_at": score.updated_at,
            "cached": False,
        }
    except Exception as e:
        raise HTTPException(502, f"Failed to fetch signal: {str(e)}")
