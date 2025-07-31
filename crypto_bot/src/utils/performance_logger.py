from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from .logger import LoggerMixin


class PerformanceLogger(LoggerMixin):
    """Specialized logger for performance metrics."""

    def __init__(self, log_file: str = "logs/performance.log") -> None:
        super().__init__()
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s %(message)s")
        handler.setFormatter(formatter)
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_calculation_performance(
        self, operation: str, time_ms: int, target_ms: int | None = None
    ) -> None:
        self.logger.info(
            "calculation_performance", operation=operation, time_ms=time_ms, target_ms=target_ms
        )

    def log_real_time_metrics(self, metrics: Dict[str, Any]) -> None:
        self.logger.info("real_time_metrics", **metrics)

    def log_performance_bottleneck(self, operation: str, time_ms: int) -> None:
        self.logger.warning("performance_bottleneck", operation=operation, time_ms=time_ms)
