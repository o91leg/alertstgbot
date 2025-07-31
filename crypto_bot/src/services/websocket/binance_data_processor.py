from __future__ import annotations

"""Processing of incoming Binance WebSocket messages."""

import asyncio
from decimal import Decimal
from typing import Any, Dict

from services.cache.candle_cache import CandleCache
from utils.logger import LoggerMixin
from utils.time_helpers import timestamp_to_datetime
from utils.validators import validate_binance_kline_data_detailed
from utils.performance_utils import measure_time


class BinanceDataProcessor(LoggerMixin):
    """Transform and route Binance WebSocket data."""

    def __init__(
        self,
        candle_cache: CandleCache,
        real_time_processor: Any | None = None,
    ) -> None:
        super().__init__()
        self.candle_cache = candle_cache
        self.real_time_processor = real_time_processor

    @measure_time(target_ms=10)
    async def process_websocket_message(self, message: Dict[str, Any]) -> None:
        """Entry point for raw WebSocket messages."""

        data = message.get("data", message)
        event_type = data.get("e")
        if event_type == "kline":
            await self._process_kline_message(data)

    async def _process_kline_message(self, data: Dict[str, Any]) -> None:
        kline = data.get("k", {})
        if not validate_binance_kline_data_detailed(kline):
            return
        candle = self._convert_kline_to_candle(data["s"], kline["i"], kline)
        await self.candle_cache.add_new_candle(candle["symbol"], candle["timeframe"], candle)
        if candle["is_closed"]:
            await self._trigger_real_time_processing(candle)

    def _convert_kline_to_candle(self, symbol: str, timeframe: str, kline: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Binance kline payload to internal candle representation."""

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "open_time": timestamp_to_datetime(kline["t"]),
            "close_time": timestamp_to_datetime(kline["T"]),
            "open_price": Decimal(kline["o"]),
            "high_price": Decimal(kline["h"]),
            "low_price": Decimal(kline["l"]),
            "close_price": Decimal(kline["c"]),
            "volume": Decimal(kline["v"]),
            "is_closed": bool(kline["x"]),
        }

    async def _trigger_real_time_processing(self, candle: Dict[str, Any]) -> None:
        if self.real_time_processor is None:
            return
        asyncio.create_task(self.real_time_processor.process_websocket_data(candle))
