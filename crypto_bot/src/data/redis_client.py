from __future__ import annotations

"""Redis client with connection pooling and health checks."""

from typing import Optional

import asyncio
import redis.asyncio as redis

from config.redis_config import get_redis_config

_redis: Optional[redis.Redis] = None


async def init_redis(url: str | None = None) -> None:
    """Initialize global Redis client with connection pooling."""

    global _redis
    if _redis is None:
        config = get_redis_config()
        pool = redis.ConnectionPool.from_url(
            url or config.url,
            max_connections=config.max_connections,
            decode_responses=True,
        )
        _redis = redis.Redis(connection_pool=pool)
        try:
            await _redis.ping()
        except Exception:  # pragma: no cover - network dependent
            _redis = None
            raise


async def close_redis() -> None:
    """Close the Redis connection."""

    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis is not initialized")
    return _redis


async def test_connection() -> bool:
    try:
        client = get_redis()
        await client.ping()
        return True
    except Exception:
        # attempt reconnection
        try:
            await init_redis()
            return True
        except Exception:  # pragma: no cover - network dependent
            return False
