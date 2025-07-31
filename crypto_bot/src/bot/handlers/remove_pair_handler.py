from __future__ import annotations

"""Handlers for removing trading pairs."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from data.repositories.user_pair_repository import UserPairRepository
from services.websocket.stream_manager import StreamManager

remove_pair_router = Router()
user_pair_repository = UserPairRepository()
stream_manager: StreamManager | None = None


class RemovePairStates(StatesGroup):
    selecting_pair = State()
    confirming_removal = State()


def register_remove_pair_handlers(dp) -> None:  # type: ignore[override]
    dp.include_router(remove_pair_router)


@remove_pair_router.callback_query(F.data == "remove_pair")
async def choose_pair_to_remove(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Выберите пару для удаления (пока заглушка)")
    await state.set_state(RemovePairStates.selecting_pair)
    await callback.answer()


async def execute_pair_removal(
    session: AsyncSession, user_id: int, pair_id: int
) -> None:
    await user_pair_repository.delete(session, pair_id)
    if stream_manager:
        await stream_manager.update_subscriptions()


@remove_pair_router.callback_query(RemovePairStates.confirming_removal)
async def confirm_removal(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    pair_id = data.get("pair_id")
    if not pair_id:
        await callback.answer("Пара не найдена", show_alert=True)
        return
    await execute_pair_removal(session, callback.from_user.id, pair_id)
    await session.commit()
    await callback.message.answer("Пара удалена")
    await state.clear()
    await callback.answer()
