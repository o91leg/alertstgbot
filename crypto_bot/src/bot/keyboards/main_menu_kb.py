from __future__ import annotations

"""Inline keyboards for the main bot menu."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard(real_time_enabled: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить пару", callback_data="add_pair"),
        InlineKeyboardButton(text="📊 Мои пары", callback_data="my_pairs"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Удалить пару", callback_data="remove_pair"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
    )
    if real_time_enabled:
        rt_status = "⚡ Реальное время: ВКЛ"
        builder.row(InlineKeyboardButton(text=rt_status, callback_data="real_time_status"))
    return builder.as_markup()


def get_real_time_controls_keyboard(active: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle = "⏸ Пауза" if active else "▶️ Возобновить"
    builder.row(
        InlineKeyboardButton(text="📊 Производительность", callback_data="rt_metrics"),
        InlineKeyboardButton(text="⚙️ Настройки RT", callback_data="rt_settings"),
    )
    builder.row(InlineKeyboardButton(text=toggle, callback_data="rt_toggle"))
    builder.row(InlineKeyboardButton(text="🔧 Диагностика", callback_data="rt_diag"))
    return builder.as_markup()


def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="notif"),
        InlineKeyboardButton(text="🕐 Интервалы", callback_data="intervals"),
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Реальное время", callback_data="rt_settings"),
        InlineKeyboardButton(text="📈 Статистика", callback_data="stats"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        InlineKeyboardButton(text="ℹ️ О боте", callback_data="about"),
    )
    return builder.as_markup()


def get_confirmation_keyboard(yes: str, no: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=yes),
        InlineKeyboardButton(text="❌ Нет", callback_data=no),
    )
    return builder.as_markup()
