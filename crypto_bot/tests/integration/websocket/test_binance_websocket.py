import json

import pytest
from src.services.websocket.binance_websocket import (
    BinanceWebSocketClient,
    ConnectionState,
)
from src.utils.time_helpers import get_high_precision_timestamp

pytestmark = pytest.mark.skip(reason="requires real Binance WebSocket")


@pytest.mark.asyncio
async def test_websocket_connection():
    client = BinanceWebSocketClient(config=None)  # type: ignore[arg-type]
    connected = await client.connect()
    assert connected  # pragma: no cover - network
    assert client.get_connection_state() == ConnectionState.CONNECTED
    await client.disconnect()
    assert client.get_connection_state() == ConnectionState.DISCONNECTED


@pytest.mark.asyncio
async def test_message_processing_performance():
    client = BinanceWebSocketClient(config=None)  # type: ignore[arg-type]
    test_message = {
        "e": "kline",
        "E": 123456789,
        "s": "BTCUSDT",
        "k": {
            "t": 123400000,
            "T": 123460000,
            "s": "BTCUSDT",
            "i": "1m",
            "o": "45000.00",
            "c": "45100.00",
            "h": "45150.00",
            "l": "44950.00",
            "v": "1000",
            "x": True,
        },
    }
    processing_times = []
    for _ in range(100):
        start = get_high_precision_timestamp()
        await client.handle_message(json.dumps(test_message))
        end = get_high_precision_timestamp()
        processing_times.append(end - start)
    avg = sum(processing_times) / len(processing_times)
    assert avg < 10
