from __future__ import annotations

"""Handlers for managing user's trading pairs."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.cache.indicator_cache import indicator_cache
from .my_pairs_formatters import (
    create_pairs_list_message,
    create_real_time_performance_message,
)
from .my_pairs_keyboards import (
    create_pair_management_keyboard,
    create_real_time_status_keyboard,
)

my_pairs_router = Router()


class MyPairsStates(StatesGroup):
    viewing_pairs = State()
    managing_timeframes = State()
    viewing_rsi = State()
    viewing_real_time_status = State()


def register_my_pairs_handlers(dp) -> None:  # type: ignore[override]
    dp.include_router(my_pairs_router)


@my_pairs_router.callback_query(F.data == "my_pairs")
async def show_user_pairs(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    # Placeholder: repository method not implemented, send empty list
    user_pairs: list[dict] = []
    text = (
        create_pairs_list_message(user_pairs)
        if user_pairs
        else "У вас пока нет добавленных пар"
    )
    await callback.message.answer(text)
    await state.set_state(MyPairsStates.viewing_pairs)
    await callback.answer()


@my_pairs_router.callback_query(MyPairsStates.viewing_pairs)
async def manage_pair(callback: CallbackQuery, state: FSMContext) -> None:
    # Expect callback data like "pair:<id>"
    parts = (callback.data or "").split(":")
    if len(parts) != 2:
        await callback.answer()
        return
    pair_id = int(parts[1])
    await callback.message.answer(
        "Управление парой",
        reply_markup=create_pair_management_keyboard(pair_id),
    )
    await callback.answer()


@my_pairs_router.callback_query(MyPairsStates.viewing_rsi)
async def show_rsi_values(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    pair_id = data.get("pair_id")
    rsi_values = indicator_cache.get_rsi(pair_id) if pair_id else {}
    lines = [f"RSI {tf}: {value}" for tf, value in rsi_values.items()]
    await callback.message.answer("\n".join(lines) or "Нет данных")
    await callback.answer()


@my_pairs_router.callback_query(MyPairsStates.viewing_real_time_status)
async def show_real_time_status(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    pair_id = data.get("pair_id")
    stats = {}  # Placeholder for performance stats
    text = create_real_time_performance_message(stats)
    await callback.message.answer(
        text, reply_markup=create_real_time_status_keyboard(pair_id or 0, True)
    )
    await callback.answer()
