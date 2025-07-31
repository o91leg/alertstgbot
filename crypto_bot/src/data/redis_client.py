from __future__ import annotations

"""Redis client with connection pooling and health checks."""

from typing import Optional

import asyncio
import redis.asyncio as redis

_redis: Optional[redis.Redis] = None


async def init_redis(url: str = "redis://localhost:6379/0") -> None:
    """Initialize global Redis client."""

    global _redis
    if _redis is None:
        _redis = redis.from_url(url, decode_responses=True)
        try:
            await _redis.ping()
        except Exception:
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
        return False
