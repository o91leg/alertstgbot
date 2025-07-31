from __future__ import annotations

"""Handlers for adding trading pairs."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config.bot_config import BotConfig
from .add_pair_logic import execute_add_pair, process_symbol_input

add_pair_router = Router()
config = BotConfig()


class AddPairStates(StatesGroup):
    waiting_for_symbol = State()
    confirming_pair = State()


def register_add_pair_handlers(dp) -> None:  # type: ignore[override]
    dp.include_router(add_pair_router)


@add_pair_router.callback_query(F.data == "add_pair")
async def start_add_pair(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Введите символ торговой пары (например BTCUSDT):")
    await state.set_state(AddPairStates.waiting_for_symbol)
    await callback.answer()


@add_pair_router.message(AddPairStates.waiting_for_symbol)
async def process_symbol_message(message: Message, state: FSMContext) -> None:
    symbol = message.text or ""
    result = await process_symbol_input(symbol)
    if not result["valid"]:
        await message.answer(result["error"])
        return
    await state.update_data(symbol=result["pair_info"]["symbol"])
    await message.answer(
        f"Добавить пару {result['pair_info']['symbol']}?", reply_markup=None
    )
    await state.set_state(AddPairStates.confirming_pair)


@add_pair_router.callback_query(AddPairStates.confirming_pair, F.data == "confirm_add_pair")
async def confirm_add_pair(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    symbol = data.get("symbol")
    if not symbol:
        await callback.answer("Символ не найден", show_alert=True)
        return
    user = callback.from_user
    pair = await execute_add_pair(session, user, symbol)  # type: ignore[arg-type]
    await session.commit()
    await callback.message.answer(f"Пара {pair.symbol} добавлена")
    await state.clear()
    await callback.answer()
