from __future__ import annotations

from typing import Any, Dict, List

from utils.logger import LoggerMixin
from utils.constants import INDICATOR_CALCULATION_TIMEOUTS, PERFORMANCE_ALERT_THRESHOLDS
from utils.time_helpers import get_high_precision_timestamp, get_time_since_ms


class PerformanceMonitor(LoggerMixin):
    """Monitor execution times and alert on slow operations."""

    def __init__(self) -> None:
        super().__init__()
        self.times: Dict[str, List[int]] = {}

    def start_timing(self) -> float:
        return get_high_precision_timestamp()

    def end_timing(self, operation: str, start: float) -> int:
        elapsed = int(get_time_since_ms(start))
        self.record_processing_time(operation, elapsed)
        return elapsed

    def record_processing_time(self, operation: str, time_ms: int) -> None:
        self.times.setdefault(operation, []).append(time_ms)

    def check_performance_targets(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for op, values in self.times.items():
            target = INDICATOR_CALCULATION_TIMEOUTS.get(op)
            if target is None:
                continue
            avg = sum(values) / len(values)
            results[op] = avg <= target
        return results

    def get_bottlenecks(self) -> Dict[str, int]:
        return {op: max(times) for op, times in self.times.items()}

    def alert_on_performance_degradation(self) -> Dict[str, Any]:
        alerts = {}
        for op, values in self.times.items():
            target = INDICATOR_CALCULATION_TIMEOUTS.get(op)
            if target is None:
                continue
            avg = sum(values) / len(values)
            if avg > target * PERFORMANCE_ALERT_THRESHOLDS["warning"]:
                alerts[op] = avg
                self.logger.warning("performance_degradation", operation=op, avg_ms=avg)
        return alerts
