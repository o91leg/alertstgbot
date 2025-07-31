from __future__ import annotations

"""Simplified Telegram notification sender."""

from typing import Any, Dict, List, Tuple

from utils.logger import LoggerMixin
from utils.performance_utils import measure_time


class TelegramSender(LoggerMixin):
    """Send notifications to Telegram users."""

    def __init__(self) -> None:  # noqa: D401 - short
        super().__init__()
        self._delivery_times: List[int] = []

    @measure_time(target_ms=500)
    async def send_signal_notification_real_time(
        self, user_id: int, message: str
    ) -> Tuple[bool, int]:
        """Send ``message`` to ``user_id`` and return success flag and time."""

        # In real implementation this would call Telegram API.
        return True, 0

    async def send_message_to_user(self, user_id: int, message: str) -> bool:
        success, ms = await self.send_signal_notification_real_time(user_id, message)
        if success:
            self._delivery_times.append(ms)
        return success

    async def send_bulk_real_time_notifications(
        self, notifications: List[Dict[str, Any]]
    ) -> None:
        for note in notifications:
            await self.send_message_to_user(note["user_id"], note["message"])

    def handle_blocked_user(self, user_id: int) -> None:
        self.logger.warning("user_blocked", user_id=user_id)

    def get_real_time_delivery_stats(self) -> Dict[str, float]:
        if not self._delivery_times:
            return {}
        avg = sum(self._delivery_times) / len(self._delivery_times)
        return {"avg_delivery_ms": avg, "max_delivery_ms": max(self._delivery_times)}
