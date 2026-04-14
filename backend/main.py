"""
Zerova API Server — FastAPI Entrypoint.

Main REST API serving the Zerova frontend and external integrations.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.vault import router as vault_router
from api.routes.user import router as user_router
from api.routes.signal import router as signal_router
from api.middleware.rate_limit import RateLimitMiddleware
from db.queries import init_db
from db.connection import close_connections


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_connections()


app = FastAPI(
    title="Zerova Protocol API",
    description="Delta-neutral yield protocol built on Pacifica perpetuals",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://zerova.fi"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Register routes
app.include_router(vault_router)
app.include_router(user_router)
app.include_router(signal_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "zerova-api"}
