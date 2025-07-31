from __future__ import annotations

"""Priority queue for outgoing notifications."""

import asyncio
from typing import Any, Dict, Tuple

from utils.logger import LoggerMixin


class NotificationQueue(LoggerMixin):
    """Maintain a priority queue for real-time notifications."""

    def __init__(self) -> None:  # noqa: D401 - short
        super().__init__()
        self._queue: "asyncio.PriorityQueue[Tuple[int, Dict[str, Any]]]" = asyncio.PriorityQueue()

    async def add_real_time_notification(
        self, notification: Dict[str, Any], priority: int = 0
    ) -> None:
        """Add ``notification`` with ``priority`` (lower value = higher priority)."""

        await self._queue.put((priority, notification))

    async def process_notifications(self, handler) -> None:
        """Process all queued notifications using ``handler`` coroutine."""

        while not self._queue.empty():
            priority, item = await self._queue.get()
            try:
                await handler(item)
            finally:
                self._queue.task_done()

    def get_real_time_queue_size(self) -> int:
        """Return current queue size."""

        return self._queue.qsize()

    async def retry_failed_notifications(self) -> None:
        """Placeholder for retry logic."""

        return None
