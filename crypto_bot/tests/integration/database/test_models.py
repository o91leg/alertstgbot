import pytest

pytestmark = pytest.mark.skip(reason="database tests require PostgreSQL")


@pytest.mark.asyncio
async def test_user_model_operations(db_session):
    from src.data.models.user import User

    user = User(
        id=123456789,
        username="test_user",
        first_name="Test",
        last_name="User",
        language_code="en",
        notifications_enabled=True,
        is_active=True,
        real_time_enabled=True,
    )
    db_session.add(user)
    await db_session.commit()
    retrieved = await db_session.get(User, 123456789)
    assert retrieved.username == "test_user"
    retrieved.notifications_enabled = False
    retrieved.increment_signals_count()
    await db_session.commit()
    updated = await db_session.get(User, 123456789)
    assert updated.notifications_enabled is False
    assert updated.total_signals_received == 1


@pytest.mark.asyncio
async def test_user_pair_relationships(db_session):
    from src.data.models.pair import Pair
    from src.data.models.user import User
    from src.data.models.user_pair import UserPair

    user = User(id=123, username="test", first_name="Test")
    pair = Pair(symbol="BTCUSDT", base_asset="BTC", quote_asset="USDT")
    db_session.add_all([user, pair])
    await db_session.commit()
    link = UserPair(
        user_id=user.id,
        pair_id=pair.id,
        timeframes={"1m": True, "5m": True, "1h": False},
        real_time_active=True,
    )
    db_session.add(link)
    await db_session.commit()
    user_with_pairs = await db_session.get(User, 123)
    assert len(user_with_pairs.user_pairs) == 1
    assert user_with_pairs.user_pairs[0].pair.symbol == "BTCUSDT"
