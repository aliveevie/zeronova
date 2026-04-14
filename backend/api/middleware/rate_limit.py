"""
Rate Limiting Middleware.

Simple in-memory rate limiter using Redis for distributed deployments.
Limits requests per wallet address / IP.
"""

import time
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from db.connection import get_redis

logger = logging.getLogger(__name__)

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 60  # per window
RATE_LIMIT_PREFIX = "zerova:ratelimit:"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Use wallet from query/body or fall back to IP
        client_id = request.client.host if request.client else "unknown"

        try:
            redis = await get_redis()
            key = f"{RATE_LIMIT_PREFIX}{client_id}"
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, RATE_LIMIT_WINDOW)

            if current > RATE_LIMIT_MAX_REQUESTS:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Try again later.",
                )
        except HTTPException:
            raise
        except Exception:
            # If Redis is down, allow the request through
            pass

        return await call_next(request)
