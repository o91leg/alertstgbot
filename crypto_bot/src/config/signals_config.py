from __future__ import annotations

"""Configuration helpers for signal generation and delivery."""

from typing import Dict

from pydantic import BaseSettings, Field

from src.utils.constants import SIGNAL_REPEAT_INTERVALS


class SignalsConfig(BaseSettings):
    """Settings controlling signal thresholds and limits."""

    rsi_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {"oversold": 30.0, "overbought": 70.0}
    )
    signal_repeat_intervals: Dict[str, int] = Field(
        default_factory=lambda: SIGNAL_REPEAT_INTERVALS
    )
    max_notifications_per_hour: int = Field(default=10)
    performance_targets: Dict[str, int] = Field(
        default_factory=lambda: {
            "signal_generation": 200,
            "notification_delivery": 500,
        }
    )


def get_rsi_thresholds() -> Dict[str, float]:
    """Return configured RSI thresholds."""

    return SignalsConfig().rsi_thresholds


def get_anti_spam_intervals() -> Dict[str, int]:
    """Return intervals between repeated signals."""

    return SignalsConfig().signal_repeat_intervals


def get_performance_targets() -> Dict[str, int]:
    """Return performance targets for real-time processing."""

    return SignalsConfig().performance_targets


def validate_signal_config() -> None:
    """Placeholder for future configuration validation."""

    SignalsConfig()  # Instantiation will validate settings
