from __future__ import annotations

"""Keyboards for managing user pairs."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.constants import EMOJI


def create_pair_management_keyboard(pair_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 RSI значения", callback_data=f"rsi:{pair_id}"),
        InlineKeyboardButton(text="⚙️ Таймфреймы", callback_data=f"tf:{pair_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Реальное время", callback_data=f"rt:{pair_id}"),
        InlineKeyboardButton(text="📈 Производительность", callback_data=f"perf:{pair_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Удалить пару", callback_data=f"del:{pair_id}"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="my_pairs"),
    )
    return builder.as_markup()


def create_real_time_status_keyboard(pair_id: int, active: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle = "⏸ Пауза" if active else "▶️ Возобновить"
    builder.row(
        InlineKeyboardButton(text=toggle, callback_data=f"toggle_rt:{pair_id}"),
        InlineKeyboardButton(text="📊 Метрики", callback_data=f"metrics:{pair_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔧 Настройки", callback_data=f"rt_settings:{pair_id}"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="my_pairs"),
    )
    return builder.as_markup()
