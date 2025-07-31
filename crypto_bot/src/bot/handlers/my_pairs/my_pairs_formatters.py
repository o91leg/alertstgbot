from __future__ import annotations

"""Formatting helpers for the ``my_pairs`` handlers."""

from typing import Any, Dict, List

from utils.time_helpers import format_datetime


def create_pairs_list_message(user_pairs: List[Dict[str, Any]]) -> str:
    message = "📊 <b>Ваши торговые пары:</b>\n\n"
    for pair_data in user_pairs:
        symbol = pair_data["symbol"]
        signals_count = pair_data.get("signals_count", 0)
        last_signal = pair_data.get("last_signal_time")
        real_time_status = (
            "⚡ Активно" if pair_data.get("real_time_active") else "⏸ Пауза"
        )
        message += f"💰 <b>{symbol}</b>\n"
        message += f"📈 Сигналов: {signals_count}\n"
        message += f"🔥 Реальное время: {real_time_status}\n"
        if last_signal:
            message += f"🕐 Последний: {format_datetime(last_signal)}\n"
        message += "\n"
    return message


def create_real_time_performance_message(stats: Dict[str, Any]) -> str:
    """Create a simple text representation of performance metrics."""

    lines = ["⚡ <b>Производительность реального времени</b>"]
    for key, value in stats.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
