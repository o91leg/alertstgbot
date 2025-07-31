from __future__ import annotations

"""Redis cache configuration."""

from pydantic import BaseSettings, Field


class RedisConfig(BaseSettings):
    """Settings for Redis connections and TTLs."""

    url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    candle_ttl: int = Field(default=600, description="TTL for candle data in seconds")
    indicator_ttl: int = Field(
        default=30, description="TTL for indicator values in seconds"
    )
    realtime_ttl: int = Field(default=10, description="TTL for real-time prices")
    state_ttl: int = Field(default=300, description="TTL for indicator states")
    metrics_ttl: int = Field(default=60, description="TTL for metrics data")


def get_redis_config() -> RedisConfig:
    """Return configuration instance."""

    return RedisConfig()
