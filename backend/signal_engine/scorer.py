"""
Signal Scorer.

Computes the Funding Rate Sentiment Score (FRSS) by aggregating
multiple Elfa AI data points into a single 0.0-1.0 score used
by the rebalancer to make position adjustment decisions.

FRSS Range | Sentiment          | Action
0.75-1.0   | Strong bullish     | Hold short perp — max funding collection
0.50-0.75  | Mild bullish       | Hold — monitor every epoch
0.30-0.50  | Neutral/uncertain  | Reduce perp exposure by 25%
0.00-0.30  | Bearish/risk       | Full exit to PARKED state
"""

import logging
import time
from signal_engine.elfa_client import ElfaSignalEngine, SignalScore

logger = logging.getLogger(__name__)


class SignalScorer:
    def __init__(self, elfa: ElfaSignalEngine):
        self.elfa = elfa

    async def compute_frss(self, asset: str) -> SignalScore:
        """
        Compute composite Funding Rate Sentiment Score for an asset.

        Combines:
        - Social mention volume (normalized)
        - Sentiment from top mentions
        - Funding rate keyword context
        """
        mention_score = 0.5
        volume_score = 0
        trend = "stable"
        social_volume = 0
        confidence = 0.3  # default low confidence

        try:
            # Fetch top mentions for the asset
            mentions_data = await self.elfa.get_top_mentions(asset)
            mentions = mentions_data.get("data", {}).get("mentions", [])

            if mentions:
                social_volume = len(mentions)
                # Score based on engagement — high engagement on an asset
                # implies bullish sentiment (longs pay shorts, good for our short)
                total_engagement = sum(
                    m.get("smartEngagement", 0) or m.get("engagement", 0)
                    for m in mentions
                )
                # Normalize: more engagement = more bullish sentiment
                if total_engagement > 1000:
                    mention_score = min(0.9, 0.5 + (total_engagement / 50000))
                elif total_engagement > 100:
                    mention_score = 0.5 + (total_engagement / 10000)
                else:
                    mention_score = 0.4

                confidence = min(0.9, 0.3 + (social_volume / 100))
        except Exception as e:
            logger.warning(f"Failed to fetch mentions for {asset}: {e}")

        try:
            # Check funding rate context via keyword search
            funding_data = await self.elfa.get_keyword_mentions(
                keywords=f"{asset} funding rate", limit=20
            )
            funding_mentions = funding_data.get("data", {}).get("mentions", [])

            if len(funding_mentions) > 10:
                # High chatter about funding rates often precedes shifts
                volume_score = 0.1
                trend = "deteriorating" if mention_score < 0.5 else "improving"
            elif len(funding_mentions) > 3:
                volume_score = 0.05
        except Exception as e:
            logger.warning(f"Failed to fetch funding mentions for {asset}: {e}")

        # Composite score: weighted blend
        frss = (mention_score * 0.7) + (volume_score * 0.3)
        frss = max(0.0, min(1.0, frss))

        # Estimate funding rate direction from sentiment
        # Higher FRSS = more bullish = positive funding (shorts collect)
        funding_estimate = (frss - 0.5) * 0.002  # rough mapping

        if frss > 0.6 and mention_score > 0.55:
            trend = "improving"
        elif frss < 0.35:
            trend = "deteriorating"

        return SignalScore(
            asset=asset,
            frss=round(frss, 4),
            funding_rate_estimate=round(funding_estimate, 6),
            social_volume_24h=social_volume,
            sentiment_trend=trend,
            confidence=round(confidence, 4),
            updated_at=int(time.time() * 1000),
        )
