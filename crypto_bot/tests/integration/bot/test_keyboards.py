from src.bot.keyboards.main_menu_kb import get_main_menu_keyboard


def test_main_menu_keyboard():
    keyboard_disabled = get_main_menu_keyboard(real_time_enabled=False)
    buttons = [btn.text for row in keyboard_disabled.inline_keyboard for btn in row]
    assert "➕ Добавить пару" in buttons
    assert "📊 Мои пары" in buttons
    assert "❌ Удалить пару" in buttons
    assert "⚙️ Настройки" in buttons
    keyboard_enabled = get_main_menu_keyboard(real_time_enabled=True)
    rt_buttons = [btn.text for row in keyboard_enabled.inline_keyboard for btn in row]
    assert any("реальное время" in btn.lower() for btn in rt_buttons)
