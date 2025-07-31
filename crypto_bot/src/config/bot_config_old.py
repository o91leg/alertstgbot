from __future__ import annotations

"""Pydantic settings for bot configuration."""

from typing import Dict, List, Any
from pydantic_settings import BaseSettings
from pydantic import field_validator


class BotConfig(BaseSettings):
    bot_token: str
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
    request_timeout: int = 30

    # Real-time settings
    real_time_enabled: bool = True
    real_time_performance_monitoring: bool = True
    real_time_alerts_enabled: bool = True

    max_pairs_per_user: int = 50
    max_real_time_pairs: int = 20
    notification_rate_limit: int = 10

    #default_timeframes: List[str] = ["1m", "5m", "15m", "1h", "4h", "1d"]
    default_pair: str = "BTCUSDT"

    rsi_period: int = 14
    rsi_oversold_strong: float = 20
    rsi_oversold_normal: float = 30
    rsi_overbought_normal: float = 70
    rsi_overbought_strong: float = 80

    @field_validator('default_timeframes', mode='before')
    @classmethod
    def parse_default_timeframes(cls, v: Any) -> List[str]:
        """Parse timeframes from string or list"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except:
                pass
            # If not JSON, parse as comma-separated
            return [t.strip() for t in v.split(',') if t.strip()]
        # Return default if nothing works
        return ["1m", "5m", "15m", "1h", "4h", "1d"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # This is important - don't validate assignment after init
        validate_assignment = False
        # Ignore extra fields in .env
        extra = 'ignore'

    # Helper methods
    def get_rsi_zones(self) -> Dict[str, float]:
        return {
            "oversold_strong": self.rsi_oversold_strong,
            "oversold": self.rsi_oversold_normal,
            "overbought": self.rsi_overbought_normal,
            "overbought_strong": self.rsi_overbought_strong,
        }

    def validate_config(self) -> None:
        if not self.bot_token:
            raise ValueError("Bot token is required")

    def is_real_time_enabled(self) -> bool:
        return self.real_time_enabled

    def get_performance_targets(self) -> Dict[str, int]:
        return {
            "websocket_processing": 10,
            "rsi_calculation": 100,
            "ema_calculation": 50,
            "signal_generation": 200,
            "notification_delivery": 500,
            "total_processing": 1000,
        }