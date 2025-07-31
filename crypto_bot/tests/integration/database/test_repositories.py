import pytest

pytestmark = pytest.mark.skip(reason="database tests require PostgreSQL")


@pytest.mark.asyncio
async def test_user_repository_performance(db_session):
    from src.data.repositories.user_repository import UserRepository

    repo = UserRepository(db_session)
    users_data = [
        {
            "id": i,
            "username": f"user_{i}",
            "first_name": f"User{i}",
            "real_time_enabled": i % 2 == 0,
        }
        for i in range(1000)
    ]
    await repo.bulk_create(users_data)
    rt_users = await repo.get_users_with_real_time()
    assert len(rt_users) == 500
