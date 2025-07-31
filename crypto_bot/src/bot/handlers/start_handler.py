from __future__ import annotations

"""Handlers for the ``/start`` command."""

from typing import Any, Dict, Tuple

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.bot_config import BotConfig
from src.data.models import User
from src.data.repositories.pair_repository import PairRepository
from src.data.repositories.user_pair_repository import UserPairRepository
from src.data.repositories.user_repository import UserRepository
from src.services.websocket.stream_manager import StreamManager
from src.bot.keyboards.main_menu_kb import get_main_menu_keyboard
from src.config.binance_config import get_binance_config

start_router = Router()

user_repository = UserRepository()
pair_repository = PairRepository()
user_pair_repository = UserPairRepository()
config = BotConfig()

# Global instance, expected to be set on application init
stream_manager: StreamManager | None = None


def register_start_handlers(dp) -> None:  # type: ignore[override]
    """Register start command handlers."""

    dp.include_router(start_router)


async def get_or_create_user(
    session: AsyncSession, telegram_user: Any
) -> Tuple[User, bool]:
    """Fetch existing user or create a new one."""

    user = await user_repository.get_by_telegram_id(session, telegram_user.id)
    created = False
    if not user:
        data: Dict[str, Any] = {
            "id": telegram_user.id,
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "language_code": telegram_user.language_code,
        }
        user = await user_repository.create(session, data)
        created = True
    else:
        user.update_from_telegram(telegram_user)
    return user, created


async def setup_default_pair_for_user(
    session: AsyncSession, user: User
) -> None:
    """Create default trading pair for ``user`` if missing."""

    symbol = config.default_pair
    pair = await pair_repository.get_by_symbol(session, symbol)
    if not pair:
        pair = await pair_repository.create(session, {"symbol": symbol})
    timeframes = {tf: True for tf in config.default_timeframes}
    await user_pair_repository.create(
        session,
        {
            "user_id": user.id,
            "pair_id": pair.id,
            "timeframes": timeframes,
            "real_time_active": config.real_time_enabled,
        },
    )

    if config.real_time_enabled and stream_manager:
        await stream_manager.add_symbol_stream(symbol, config.default_timeframes)


async def initialize_real_time_monitoring(user: User) -> None:
    """Enable real-time monitoring for the user if configured."""

    if not config.real_time_enabled:
        return
    user.enable_real_time_monitoring()


def create_welcome_message(user: User) -> str:
    return (
        "👋 Привет, {name}!\n"
        "Мы настроили для тебя пару по умолчанию {pair}."
    ).format(name=user.display_name, pair=config.default_pair)


def create_welcome_back_message(user: User) -> str:
    return f"С возвращением, {user.display_name}!"


@start_router.message(CommandStart())
async def handle_start_command(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Handle the ``/start`` command."""

    telegram_user = message.from_user
    if telegram_user is None:
        return

    user, created = await get_or_create_user(session, telegram_user)
    if created:
        await setup_default_pair_for_user(session, user)
        greeting = create_welcome_message(user)
    else:
        greeting = create_welcome_back_message(user)

    await initialize_real_time_monitoring(user)
    await session.commit()

    await message.answer(
        greeting, reply_markup=get_main_menu_keyboard(user.real_time_enabled)
    )
