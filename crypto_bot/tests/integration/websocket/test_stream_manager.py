import pytest
from src.services.websocket.stream_manager import StreamManager

pytestmark = pytest.mark.skip(reason="requires WebSocket and database setup")


@pytest.mark.asyncio
async def test_subscription_management():
    manager = StreamManager(None, None, None, None)  # type: ignore[arg-type]
    await manager.start()
    success = await manager.add_symbol_stream("BTCUSDT", ["1m", "5m"])
    assert success  # pragma: no cover - placeholder
    active = await manager.get_active_streams()
    expected = ["btcusdt@kline_1m", "btcusdt@kline_5m", "btcusdt@ticker"]
    for stream in expected:
        assert stream in active
    success = await manager.remove_symbol_stream("BTCUSDT")
    assert success
    await manager.stop()
