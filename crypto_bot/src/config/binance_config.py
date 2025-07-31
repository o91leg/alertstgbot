from __future__ import annotations

"""Configuration for Binance API and WebSocket settings."""

from pydantic_settings import BaseSettings
from pydantic import Field


class BinanceConfig(BaseSettings):
    """Settings controlling Binance connections."""

    websocket_url: str = Field(
        default="wss://stream.binance.com:9443/ws", description="WebSocket base URL"
    )
    api_url: str = Field(
        default="https://api.binance.com", description="REST API base URL"
    )
    ping_interval: int = Field(default=20, description="Ping interval in seconds")
    reconnect_max_attempts: int = Field(default=5, description="Max reconnect tries")
    reconnect_max_delay: int = Field(
        default=60, description="Maximum backoff delay in seconds"
    )
    subscription_update_interval: int = Field(
        default=60, description="Interval to refresh subscriptions"
    )


def get_binance_config() -> BinanceConfig:
    """Return configuration instance."""

    return BinanceConfig()
