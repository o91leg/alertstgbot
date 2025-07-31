from __future__ import annotations

"""Collect and store system and performance metrics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

import psutil

from data.redis_client import get_redis
from utils.time_helpers import get_current_timestamp


@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int


@dataclass
class PerformanceMetrics:
    timestamp: datetime
    websocket_latency_ms: int
    rsi_calculation_ms: int
    ema_calculation_ms: int
    signal_generation_ms: int
    notification_delivery_ms: int
    total_processing_ms: int


class MetricsCollector:
    """Collect metrics and store in Redis time-series structures."""

    def __init__(self) -> None:
        self.redis = get_redis()

    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().used / 1024 / 1024
        net = psutil.net_io_counters()
        disk = psutil.disk_io_counters()
        metrics = {
            "cpu_percent": cpu,
            "memory_mb": mem,
            "disk_io_read": disk.read_bytes,
            "disk_io_write": disk.write_bytes,
            "network_sent": net.bytes_sent,
            "network_recv": net.bytes_recv,
        }
        await self.store_metrics(metrics)
        return metrics

    async def store_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store metrics in Redis sorted sets."""

        timestamp = get_current_timestamp()
        for metric_name, value in metrics.items():
            key = f"metrics:{metric_name}"
            await self.redis.zadd(key, {str(value): timestamp})
            cutoff = timestamp - 86400
            await self.redis.zremrangebyscore(key, 0, cutoff)

    async def generate_performance_report(self) -> Dict[str, Any]:  # pragma: no cover - placeholder
        return {}

    async def create_real_time_dashboard(self) -> None:  # pragma: no cover - placeholder
        pass
