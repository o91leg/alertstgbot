from __future__ import annotations

"""RSI signal generator used in real-time processing."""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.signal_repository import SignalRepository
from src.data.repositories.user_repository import UserRepository
from src.services.signals.anti_spam import AntiSpamManager
from src.services.notifications.notification_queue import NotificationQueue
from src.utils.logger import LoggerMixin
from src.utils.performance_utils import measure_time
from src.utils.constants import RSI_ZONES


class RSIZone(Enum):
    STRONG_OVERSOLD = "strong_oversold"
    MEDIUM_OVERSOLD = "medium_oversold"
    NORMAL_OVERSOLD = "normal_oversold"
    NEUTRAL = "neutral"
    NORMAL_OVERBOUGHT = "normal_overbought"
    MEDIUM_OVERBOUGHT = "medium_overbought"
    STRONG_OVERBOUGHT = "strong_overbought"


class RSISignalGenerator(LoggerMixin):
    """Generate RSI based signals and enqueue notifications."""

    def __init__(self) -> None:  # noqa: D401 - short
        super().__init__()
        self._signal_repo = SignalRepository()
        self._user_repo = UserRepository()
        self._anti_spam = AntiSpamManager()
        self._notification_queue = NotificationQueue()
        self._previous_rsi: Dict[Tuple[str, str], float] = {}

    @measure_time(target_ms=200)
    async def process_rsi_update_real_time(
        self,
        session: AsyncSession,
        symbol: str,
        timeframe: str,
        rsi_value: float,
        price: float,
        processing_time_ms: int,
        volume_change_percent: Optional[float] = None,
    ) -> int:
        prev_rsi = self._previous_rsi.get((symbol, timeframe))
        signals = await self.check_rsi_signals_real_time(
            session,
            symbol,
            timeframe,
            rsi_value,
            prev_rsi,
            price,
            volume_change_percent,
        )
        count = 0
        if signals:
            count = await self.generate_real_time_notifications(
                session, signals, processing_time_ms
            )
        self._previous_rsi[(symbol, timeframe)] = rsi_value
        return count

    async def check_rsi_signals_real_time(
        self,
        session: AsyncSession,
        symbol: str,
        timeframe: str,
        current_rsi: float,
        previous_rsi: Optional[float],
        current_price: float,
        volume_change_percent: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Analyse RSI values and return signal payloads."""

        signal_type = self._determine_rsi_signal_type_with_trend(
            current_rsi, previous_rsi
        )
        if not signal_type:
            return []
        return [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "signal_type": signal_type,
                "price": current_price,
                "rsi_value": current_rsi,
            }
        ]

    def _determine_rsi_signal_type_with_trend(
        self, current_rsi: float, previous_rsi: Optional[float]
    ) -> Optional[str]:
        if previous_rsi is None:
            return None
        if current_rsi < 30 and previous_rsi >= 30:
            return "rsi_oversold_entry"
        if current_rsi >= 30 and previous_rsi < 30:
            return "rsi_oversold_exit"
        if current_rsi > 70 and previous_rsi <= 70:
            return "rsi_overbought_entry"
        if current_rsi <= 70 and previous_rsi > 70:
            return "rsi_overbought_exit"
        if current_rsi < 20 and previous_rsi >= 20:
            return "rsi_strong_oversold"
        if current_rsi > 80 and previous_rsi <= 80:
            return "rsi_strong_overbought"
        return None

    async def generate_real_time_notifications(
        self,
        session: AsyncSession,
        signals: List[Dict[str, Any]],
        processing_time_ms: int,
    ) -> int:
        """Create notifications for users and persist history."""

        total = 0
        for signal in signals:
            users = await self._get_users_for_notification(
                session, signal["symbol"], signal["timeframe"]
            )
            for user_id in users:
                if not await self._can_send_signal(
                    user_id,
                    signal["symbol"],
                    signal["timeframe"],
                    signal["signal_type"],
                    signal.get("rsi_value"),
                ):
                    continue
                payload = {
                    **signal,
                    "user_id": user_id,
                    "processing_time_ms": processing_time_ms,
                }
                await self._notification_queue.add_real_time_notification(payload)
                await self._signal_repo.save_signal_with_metrics(
                    session,
                    user_id,
                    signal["symbol"],
                    signal["timeframe"],
                    signal["signal_type"],
                    signal_value=signal.get("rsi_value"),
                    price=signal.get("price"),
                    processing_time_ms=processing_time_ms,
                )
                total += 1
        return total

    async def _get_users_for_notification(
        self, session: AsyncSession, symbol: str, timeframe: str
    ) -> List[int]:
        users = await self._user_repo.get_users_with_pair_and_timeframe(
            session, symbol, timeframe
        )
        return [u.id for u in users]

    async def _can_send_signal(
        self,
        user_id: int,
        symbol: str,
        timeframe: str,
        signal_type: str,
        rsi_value: Optional[float] = None,
    ) -> bool:
        return await self._anti_spam.can_send_signal(
            user_id, symbol, timeframe, signal_type, rsi_value=rsi_value
        )


rsi_signal_generator = RSISignalGenerator()
