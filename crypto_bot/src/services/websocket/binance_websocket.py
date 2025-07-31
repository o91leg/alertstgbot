from __future__ import annotations

"""Asynchronous WebSocket client for Binance streaming API."""

import asyncio
import json
from enum import Enum
from typing import Awaitable, Callable, List

import websockets
from websockets import WebSocketClientProtocol

from config.binance_config import BinanceConfig
from utils.logger import LoggerMixin
from utils.time_helpers import get_high_precision_timestamp, get_time_since_ms
from utils.exceptions import WebSocketConnectionError


class ConnectionState(Enum):
    """Possible states of the WebSocket connection."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    CLOSED = "closed"


class BinanceWebSocketClient(LoggerMixin):
    """Handle connection and subscriptions to Binance WebSocket streams."""

    def __init__(
        self,
        config: BinanceConfig,
        message_handler: Callable[[dict], Awaitable[None]] | None = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.message_handler = message_handler
        self.state = ConnectionState.DISCONNECTED
        self.ws: WebSocketClientProtocol | None = None
        self.ping_task: asyncio.Task[None] | None = None
        self.active_subscriptions: set[str] = set()
        self._id_counter = 0

    async def connect(self) -> None:
        """Establish WebSocket connection to Binance."""

        if self.state in {ConnectionState.CONNECTED, ConnectionState.CONNECTING}:
            return
        self.state = ConnectionState.CONNECTING
        try:
            self.ws = await websockets.connect(self.config.websocket_url, ping_interval=None)
        except Exception as exc:  # pragma: no cover - network failures
            self.state = ConnectionState.DISCONNECTED
            raise WebSocketConnectionError(str(exc)) from exc
        self.state = ConnectionState.CONNECTED
        self.ping_task = asyncio.create_task(self._ping_loop())
        asyncio.create_task(self._receive_loop())

    async def _receive_loop(self) -> None:
        assert self.ws is not None
        try:
            async for message in self.ws:
                await self.handle_message(message)
        except Exception:  # pragma: no cover - network failures
            await self.reconnect()

    async def _ping_loop(self) -> None:
        while self.state == ConnectionState.CONNECTED and self.ws is not None:
            await asyncio.sleep(self.config.ping_interval)
            try:
                await self.ws.ping()
            except Exception:  # pragma: no cover
                break
        if self.state == ConnectionState.CONNECTED:
            await self.reconnect()

    async def handle_message(self, message: str) -> None:
        """Parse a raw message and forward to handler."""

        start = get_high_precision_timestamp()
        try:
            data = json.loads(message)
        except json.JSONDecodeError as exc:
            self.logger.error("json_decode_error", error=str(exc))
            return
        if self.message_handler is not None:
            await self.message_handler(data)
        elapsed = get_time_since_ms(start)
        self.logger.debug("message_processed", elapsed_ms=elapsed)

    async def reconnect(self) -> None:
        """Reconnect with exponential backoff."""

        delay = 1
        attempts = 0
        self.state = ConnectionState.RECONNECTING
        while attempts < self.config.reconnect_max_attempts:
            await asyncio.sleep(delay)
            try:
                await self.connect()
                if self.state == ConnectionState.CONNECTED:
                    if self.active_subscriptions:
                        await self.subscribe_to_streams(list(self.active_subscriptions))
                    return
            except WebSocketConnectionError:
                attempts += 1
                delay = min(delay * 2, self.config.reconnect_max_delay)
        self.state = ConnectionState.CLOSED

    async def subscribe_to_streams(self, streams: List[str]) -> None:
        """Subscribe to Binance streams."""

        if self.state != ConnectionState.CONNECTED or self.ws is None:
            raise WebSocketConnectionError("WebSocket not connected")
        self._id_counter += 1
        msg = {"method": "SUBSCRIBE", "params": streams, "id": self._id_counter}
        await self.ws.send(json.dumps(msg))
        self.active_subscriptions.update(streams)

    async def disconnect(self) -> None:
        if self.ws is not None:
            await self.ws.close()
        if self.ping_task is not None:
            self.ping_task.cancel()
        self.state = ConnectionState.CLOSED
