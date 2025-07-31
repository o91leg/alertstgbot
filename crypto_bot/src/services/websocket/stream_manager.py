from __future__ import annotations

"""Manage Binance WebSocket streams and subscriptions."""

import asyncio
from typing import Dict, Iterable, List, Set

from sqlalchemy.ext.asyncio import async_sessionmaker

from config.binance_config import BinanceConfig
from data.repositories.user_pair_repository import UserPairRepository
from utils.logger import LoggerMixin
from utils.performance_utils import TimingContext
from .binance_websocket import BinanceWebSocketClient
from .binance_data_processor import BinanceDataProcessor


def get_kline_stream_name(symbol: str, timeframe: str) -> str:
    """Return kline stream name for ``symbol``/``timeframe``."""

    return f"{symbol.lower()}@kline_{timeframe}"


def get_ticker_stream_name(symbol: str) -> str:
    """Return ticker stream name for ``symbol``."""

    return f"{symbol.lower()}@ticker"


def parse_stream_name(stream_name: str) -> Dict[str, str]:
    """Parse combined stream name back into its components."""

    parts = stream_name.split("@")
    symbol = parts[0].upper()
    if "kline" in parts[1]:
        tf = parts[1].split("_")[1]
        return {"symbol": symbol, "type": "kline", "timeframe": tf}
    return {"symbol": symbol, "type": "ticker"}


class StreamManager(LoggerMixin):
    """High level manager for all Binance WebSocket streams."""

    def __init__(
        self,
        sessionmaker: async_sessionmaker,
        repository: UserPairRepository,
        config: BinanceConfig,
        data_processor: BinanceDataProcessor,
    ) -> None:
        super().__init__()
        self.sessionmaker = sessionmaker
        self.repository = repository
        self.config = config
        self.data_processor = data_processor
        self.websocket: BinanceWebSocketClient | None = None
        self.active_streams: Set[str] = set()

    async def start(self) -> None:
        """Start the WebSocket client and subscription updater."""

        self.websocket = BinanceWebSocketClient(
            self.config, message_handler=self.handle_websocket_message
        )
        await self.websocket.connect()
        asyncio.create_task(self._periodic_subscription_update())

    async def _periodic_subscription_update(self) -> None:
        while True:
            await self.update_subscriptions()
            await asyncio.sleep(self.config.subscription_update_interval)

    async def add_symbol_stream(self, symbol: str, timeframes: Iterable[str]) -> None:
        streams: List[str] = [get_ticker_stream_name(symbol)]
        for tf in timeframes:
            streams.append(get_kline_stream_name(symbol, tf))
        if self.websocket:
            await self.websocket.subscribe_to_streams(streams)
        self.active_streams.update(streams)

    async def update_subscriptions(self) -> None:
        """Refresh subscriptions based on active pairs in DB."""

        async with self.sessionmaker() as session:
            symbols = await self.repository.get_active_symbols(session)
        required_streams: Set[str] = set()
        for symbol in symbols:
            required_streams.add(get_ticker_stream_name(symbol))
            required_streams.add(get_kline_stream_name(symbol, "1m"))
        new_streams = required_streams - self.active_streams
        if new_streams and self.websocket:
            await self.websocket.subscribe_to_streams(list(new_streams))
        self.active_streams.update(new_streams)
        removed = self.active_streams - required_streams
        if removed:
            # Unsubscribe logic could be added here.
            self.active_streams -= removed
        self.logger.debug("subscriptions_updated", new=len(new_streams), removed=len(removed))

    async def handle_websocket_message(self, message: dict) -> None:
        """Pass incoming messages directly to the data processor."""

        with TimingContext() as tc:
            await self.data_processor.process_websocket_message(message)
        self.logger.debug("message_forwarded", elapsed_ms=tc.elapsed_ms)
