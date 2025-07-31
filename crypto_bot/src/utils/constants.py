from __future__ import annotations

from typing import Dict, List

EMA_PERIODS: List[int] = [20, 50, 100, 200]

PERFORMANCE_ALERT_THRESHOLDS = {"warning": 1.5, "critical": 2.0}

INDICATOR_CALCULATION_TIMEOUTS = {
    "websocket_processing": 10,
    "rsi_calculation": 100,
    "ema_calculation": 50,
    "signal_generation": 200,
    "notification_delivery": 500,
    "total_processing": 1000,
}

REAL_TIME_CACHE_SIZES = {
    "price": 10,
    "indicator_state": 300,
}


def get_real_time_target(operation: str) -> int:
    return INDICATOR_CALCULATION_TIMEOUTS.get(operation, 0)


def is_real_time_performance_good(time_ms: int, operation: str) -> bool:
    target = get_real_time_target(operation)
    return target == 0 or time_ms <= target


def get_performance_emoji(time_ms: int, target_ms: int) -> str:
    if target_ms == 0:
        return "⏱️"
    ratio = time_ms / target_ms if target_ms else 0
    if ratio <= 1:
        return "✅"
    if ratio <= PERFORMANCE_ALERT_THRESHOLDS["warning"]:
        return "⚠️"
    return "🚨"
