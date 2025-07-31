from __future__ import annotations

"""Batch processing utilities for heavy operations."""

from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List

import orjson
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from data.redis_client import get_redis
from utils.logger import LoggerMixin
from utils.time_helpers import get_current_timestamp


class BatchOperation(Enum):
    SAVE_CANDLES = "save_candles"
    UPDATE_INDICATORS = "update_indicators"
    SEND_NOTIFICATIONS = "send_notifications"
    SAVE_SIGNALS = "save_signals"
    UPDATE_USER_STATS = "update_user_stats"


class BatchProcessor(LoggerMixin):
    """Process queued operations in batches using Redis lists."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session
        self.redis = get_redis()

    async def add_to_batch(self, operation: BatchOperation, data: Dict[str, Any], priority: int = 0) -> None:
        """Add an operation to the batch queue."""

        batch_item = {
            "operation": operation.value,
            "data": data,
            "timestamp": get_current_timestamp(),
            "priority": priority,
        }
        queue_key = f"batch_{operation.value}"
        await self.redis.lpush(queue_key, orjson.dumps(batch_item))
        queue_size = await self.redis.llen(queue_key)
        if queue_size >= self._get_optimal_batch_size(operation):
            await self._process_batch(operation)

    async def process_batches(self) -> None:  # pragma: no cover - scheduling
        """Process all batch queues sequentially."""

        for operation in BatchOperation:
            await self._process_batch(operation)

    async def _process_batch(self, operation: BatchOperation) -> None:
        queue_key = f"batch_{operation.value}"
        items = []
        batch_size = self._get_optimal_batch_size(operation)
        for _ in range(batch_size):
            item = await self.redis.rpop(queue_key)
            if not item:
                break
            items.append(orjson.loads(item))
        if not items:
            return
        if operation == BatchOperation.SAVE_CANDLES:
            await self._process_candles_batch([i["data"] for i in items])

    async def _process_candles_batch(self, candles: List[Dict]) -> int:
        """Batch save candles to the database."""

        if not candles:
            return 0
        grouped = defaultdict(list)
        for candle in candles:
            key = (candle["symbol"], candle["timeframe"])
            grouped[key].append(candle)
        saved_count = 0
        async with self.session.begin():
            for (symbol, timeframe), group in grouped.items():
                model = self._candle_model(symbol)
                await self.session.execute(insert(model), [self._candle_to_dict(c) for c in group])
                saved_count += len(group)
        return saved_count

    def _get_optimal_batch_size(self, operation: BatchOperation) -> int:
        if operation == BatchOperation.SAVE_CANDLES:
            return 100
        if operation == BatchOperation.UPDATE_INDICATORS:
            return 50
        if operation == BatchOperation.SEND_NOTIFICATIONS:
            return 20
        return 100

    # placeholder helpers -------------------------------------------------
    def _group_candles(self, candles: List[Dict]) -> Dict[Any, List[Dict]]:
        grouped = defaultdict(list)
        for candle in candles:
            key = (candle.get("symbol"), candle.get("timeframe"))
            grouped[key].append(candle)
        return grouped

    def _candle_to_dict(self, candle: Dict[str, Any]) -> Dict[str, Any]:
        return candle

    def _candle_model(self, symbol: str):  # pragma: no cover - placeholder
        from data.models.candle import Candle  # type: ignore

        return Candle
