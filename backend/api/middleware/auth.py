"""
Authentication Middleware.

Validates wallet signatures for write operations.
Read endpoints are public. Write endpoints (deposit/withdraw) require
a valid wallet signature.
"""

import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Public endpoints that don't require auth
PUBLIC_PATHS = {
    "/api/v1/vault/stats",
    "/api/v1/vault/nav/history",
    "/api/v1/vault/positions",
    "/api/v1/signal/",
    "/health",
    "/docs",
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public endpoints
        if request.method == "GET" or any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # For write operations, validate wallet header
        wallet = request.headers.get("x-wallet-address")
        if not wallet:
            raise HTTPException(
                status_code=401,
                detail="Missing x-wallet-address header",
            )

        # Store wallet in request state for route handlers
        request.state.wallet = wallet

        return await call_next(request)
