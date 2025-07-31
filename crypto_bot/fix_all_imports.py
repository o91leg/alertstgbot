#!/usr/bin/env python3
"""
Скрипт для исправления ВСЕХ импортов в проекте крипто-бота.
Исправляет все виды импортов на правильные с префиксом src.
"""

import os
import re
from pathlib import Path

# Корневая директория с исходным кодом
SRC_DIR = Path("./src")

# Расширенные паттерны для поиска и замены
IMPORT_PATTERNS = [
    # from X import Y паттерны
    (r'^from config\.', 'from src.config.'),
    (r'^from data\.', 'from src.data.'),
    (r'^from services\.', 'from src.services.'),
    (r'^from utils\.', 'from src.utils.'),
    (r'^from bot\.', 'from src.bot.'),

    # import X паттерны
    (r'^import config\.', 'import src.config.'),
    (r'^import data\.', 'import src.data.'),
    (r'^import services\.', 'import src.services.'),
    (r'^import utils\.', 'import src.utils.'),
    (r'^import bot\.', 'import src.bot.'),

    # from X.Y import Z паттерны (более специфичные)
    (r'^from data\.models import', 'from src.data.models import'),
    (r'^from data\.repositories import', 'from src.data.repositories import'),
    (r'^from services\.websocket import', 'from src.services.websocket import'),
    (r'^from services\.indicators import', 'from src.services.indicators import'),
    (r'^from services\.signals import', 'from src.services.signals import'),
    (r'^from services\.notifications import', 'from src.services.notifications import'),
    (r'^from services\.cache import', 'from src.services.cache import'),
    (r'^from services\.real_time import', 'from src.services.real_time import'),
    (r'^from bot\.handlers import', 'from src.bot.handlers import'),
    (r'^from bot\.keyboards import', 'from src.bot.keyboards import'),
    (r'^from bot\.middlewares import', 'from src.bot.middlewares import'),
]


def fix_imports_in_file(filepath: Path) -> tuple[bool, list[str]]:
    """
    Исправить импорты в одном файле.
    Возвращает (было_ли_изменение, список_изменений)
    """
    changes = []

    try:
        # Читаем содержимое файла
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        new_lines = []

        for line_num, line in enumerate(lines, 1):
            original_line = line

            # Применяем все замены к строке
            for pattern, replacement in IMPORT_PATTERNS:
                if re.match(pattern, line.strip()):
                    # Сохраняем отступы
                    indent = len(line) - len(line.lstrip())
                    new_line = ' ' * indent + re.sub(pattern, replacement, line.strip()) + '\n'

                    if new_line != original_line:
                        line = new_line
                        modified = True
                        changes.append(f"  Строка {line_num}: {original_line.strip()} → {new_line.strip()}")

            new_lines.append(line)

        # Если были изменения, записываем обратно
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        return modified, changes

    except Exception as e:
        print(f"❌ Ошибка при обработке {filepath}: {e}")
        return False, []


def main():
    """Основная функция."""
    print("🔧 Начинаю исправление ВСЕХ импортов...")
    print(f"📁 Директория: {SRC_DIR.absolute()}")
    print("=" * 60)

    fixed_count = 0
    total_count = 0
    all_changes = []

    # Рекурсивно обходим все Python файлы
    for py_file in SRC_DIR.rglob("*.py"):
        # Пропускаем __pycache__
        if "__pycache__" in str(py_file):
            continue

        total_count += 1

        # Исправляем импорты
        was_fixed, changes = fix_imports_in_file(py_file)

        if was_fixed:
            rel_path = py_file.relative_to(SRC_DIR)
            print(f"\n✅ Исправлен: {rel_path}")
            for change in changes:
                print(change)
            fixed_count += 1
            all_changes.extend(changes)

    print("\n" + "=" * 60)
    print(f"📊 Обработано файлов: {total_count}")
    print(f"✏️  Исправлено файлов: {fixed_count}")
    print(f"📝 Всего изменений: {len(all_changes)}")
    print(f"✨ Без изменений: {total_count - fixed_count}")

    if fixed_count > 0:
        print("\n✅ Импорты успешно исправлены!")
        print("🚀 Теперь можно запускать Docker Compose")

        # Показываем рекомендацию по перезапуску
        print("\n📌 Рекомендуемые команды:")
        print("   docker-compose down")
        print("   docker-compose build --no-cache")
        print("   docker-compose up -d")
        print("   docker-compose logs -f app")
    else:
        print("\n✨ Все импорты уже корректны!")


if __name__ == "__main__":
    main()