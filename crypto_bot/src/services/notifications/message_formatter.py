from __future__ import annotations

"""Helpers for building human friendly notification messages."""

from typing import Any, Dict

from utils.constants import get_performance_emoji


class MessageFormatter:
    """Format messages for different types of signals."""

    def format_real_time_signal_message(self, signal: Dict[str, Any]) -> str:
        if signal.get("signal_type", "").startswith("rsi"):
            return self.format_rsi_signal(signal)
        return self.format_ema_signal(signal)

    def format_rsi_signal(self, signal: Dict[str, Any]) -> str:
        header = self.create_signal_header(signal)
        price = self.create_price_section(signal)
        perf = self.create_real_time_performance_section(signal)
        return f"{header}\n{price}\n{perf}"

    def format_ema_signal(self, signal: Dict[str, Any]) -> str:
        header = self.create_signal_header(signal)
        perf = self.create_real_time_performance_section(signal)
        return f"{header}\n{perf}"

    def create_signal_header(self, signal: Dict[str, Any]) -> str:
        symbol = signal.get("symbol")
        timeframe = signal.get("timeframe")
        signal_type = signal.get("signal_type")
        return f"🚨 {signal_type} - {symbol} ({timeframe})"

    def create_price_section(self, signal: Dict[str, Any]) -> str:
        price = signal.get("price")
        return f"💰 Price: {price}"

    def create_real_time_performance_section(self, signal: Dict[str, Any]) -> str:
        proc = signal.get("processing_time_ms", 0)
        emoji = get_performance_emoji(proc, 200)
        return f"⚡ Processing: {proc}ms {emoji}"
