from __future__ import annotations

"""Anti-spam manager ensuring signals are not sent too frequently."""

from typing import Any, Dict, Optional

import json

from src.data.redis_client import get_redis
from src.utils.constants import SIGNAL_REPEAT_INTERVALS
from src.utils.time_helpers import get_current_timestamp
from src.utils.logger import LoggerMixin


class AntiSpamManager(LoggerMixin):
    """Manage per-user signal rate limits using Redis sorted sets."""

    HISTORY_TTL = 24 * 60 * 60  # seconds

    def __init__(self) -> None:  # noqa: D401 - short
        super().__init__()
        self._redis = get_redis()
        self._operation_count = 0

    async def can_send_signal(
        self,
        user_id: int,
        symbol: str,
        timeframe: str,
        signal_type: str,
        *,
        rsi_value: Optional[float] = None,
    ) -> bool:
        """Return ``True`` if a signal can be sent to ``user_id``."""

        if self._is_critical_signal(signal_type, rsi_value):
            return True

        now = get_current_timestamp()
        key = self._build_key(user_id, symbol, timeframe, signal_type)
        interval = self._get_signal_interval(signal_type)
        last = await self._redis.zrevrange(key, 0, 0, withscores=True)
        if last:
            last_time = int(last[0][1])
            if now - last_time < interval:
                return False
        # global hourly limit
        hour_ago = now - 3600
        if await self._redis.zcount(key, hour_ago, now) >= 10:
            return False
        return True

    async def record_sent_signal(
        self,
        user_id: int,
        symbol: str,
        timeframe: str,
        signal_type: str,
        details: Dict[str, Any],
    ) -> None:
        """Record a sent signal for spam control."""

        now = get_current_timestamp()
        key = self._build_key(user_id, symbol, timeframe, signal_type)
        await self._redis.zadd(key, {json.dumps(details): now})
        await self._redis.expire(key, self.HISTORY_TTL)
        self._operation_count += 1
        if self._operation_count % 100 == 0:
            await self.cleanup_old_records(key)

    async def get_user_signal_stats(self, user_id: int) -> Dict[str, Any]:
        """Return basic statistics for ``user_id`` signal history."""

        pattern = f"signal_history:{user_id}:*"
        keys = await self._redis.keys(pattern)
        now = get_current_timestamp()
        hour_ago = now - 3600
        stats: Dict[str, Any] = {}
        for key in keys:
            count = await self._redis.zcount(key, hour_ago, now)
            stats[key] = count
        return stats

    async def cleanup_old_records(self, key: Optional[str] = None) -> None:
        """Remove entries older than 24h."""

        now = get_current_timestamp()
        if key is not None:
            await self._redis.zremrangebyscore(key, 0, now - self.HISTORY_TTL)
            return
        # clean all keys if none provided
        keys = await self._redis.keys("signal_history:*")
        for k in keys:
            await self._redis.zremrangebyscore(k, 0, now - self.HISTORY_TTL)

    def _get_signal_interval(self, signal_type: str) -> int:
        """Return repeat interval in seconds for ``signal_type``."""

        if signal_type.startswith("rsi"):
            return SIGNAL_REPEAT_INTERVALS.get("rsi", 0)
        if signal_type.startswith("ema"):
            return SIGNAL_REPEAT_INTERVALS.get("ema", 0)
        return 0

    @staticmethod
    def _is_critical_signal(signal_type: str, rsi_value: Optional[float] = None) -> bool:
        if signal_type.startswith("rsi") and rsi_value is not None:
            return rsi_value < 15 or rsi_value > 85
        if signal_type == "ema_golden_cross":
            return True
        return False

    @staticmethod
    def _build_key(user_id: int, symbol: str, timeframe: str, signal_type: str) -> str:
        return f"signal_history:{user_id}:{symbol}:{timeframe}:{signal_type}"
