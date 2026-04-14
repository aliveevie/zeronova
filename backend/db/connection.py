import asyncpg
import redis.asyncio as redis
from config import settings

_pool: asyncpg.Pool | None = None
_redis: redis.Redis | None = None


async def get_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.database_url, min_size=2, max_size=10)
    return _pool


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_connections():
    global _pool, _redis
    if _pool:
        await _pool.close()
        _pool = None
    if _redis:
        await _redis.close()
        _redis = None
