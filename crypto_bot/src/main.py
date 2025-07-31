"""
🚀 Главная точка входа крипто-бота с поддержкой реального времени

Версия: 3.0 РЕАЛЬНОЕ ВРЕМЯ
Назначение: Запуск и инициализация всех сервисов с мониторингом производительности
"""

import asyncio
import signal
import sys
from typing import Optional

from aiogram import Bot, Dispatcher
from src.bot.handlers.add_pair.add_pair_handler import register_add_pair_handlers
from src.bot.handlers.my_pairs.my_pairs_handler import register_my_pairs_handlers
from src.bot.handlers.remove_pair_handler import register_remove_pair_handlers
from src.bot.handlers.start_handler import register_start_handlers
from src.bot.middlewares.database_mw import DatabaseMiddleware
from src.config.bot_config import BotConfig
from src.services.websocket.stream_manager import StreamManager

try:
    from src.config.bot_config import get_bot_config

    _ = get_bot_config
    print("✅ Config import OK")
except ImportError as e:
    print(f"❌ Config import failed: {e}")

try:
    from src.bot.handlers.start_handler import (
        register_start_handlers as _register_start_handlers_test,
    )

    _ = _register_start_handlers_test
    print("✅ Handlers import OK")
except ImportError as e:
    print(f"❌ Handlers import failed: {e}")

# Глобальные переменные для сервисов
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None
stream_manager: Optional[StreamManager] = None
telegram_sender: Optional[object] = None
real_time_processor: Optional[object] = None
performance_monitor: Optional[object] = None


async def create_bot() -> Bot:
    """Создать и настроить экземпляр Telegram бота"""

    cfg = BotConfig()
    return Bot(cfg.bot_token, parse_mode="HTML")


async def setup_dispatcher(bot: Bot) -> Dispatcher:
    """Настроить диспетчер и зарегистрировать все обработчики"""

    dispatcher = Dispatcher()
    dispatcher.message.middleware(DatabaseMiddleware())
    register_start_handlers(dispatcher)
    register_add_pair_handlers(dispatcher)
    register_my_pairs_handlers(dispatcher)
    register_remove_pair_handlers(dispatcher)
    return dispatcher


def validate_application_config() -> None:
    """Валидировать конфигурацию всего приложения + настройки реального времени"""
    print("✅ Validating configuration...")
    # Будет реализовано в следующих блоках
    pass


def setup_signal_handlers() -> None:
    """Настроить обработчики системных сигналов (SIGINT, SIGTERM)"""

    def signal_handler(signum, frame):
        print(f"📡 Received shutdown signal: {signum}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def init_services() -> None:
    """Инициализировать все сервисы: БД, Redis, WebSocket, уведомления + реальное время"""
    print("🔧 Initializing services...")

    global stream_manager, telegram_sender, real_time_processor, performance_monitor

    try:
        # Инициализация БД
        from src.data.database import init_database
        await init_database()
        print("✅ Database initialized")

        # Инициализация Redis
        from src.data.redis_client import init_redis
        await init_redis()
        print("✅ Redis initialized")

        # Заглушки для сервисов (будут реализованы позже)
        stream_manager = None
        telegram_sender = None
        real_time_processor = None
        performance_monitor = None

        print("✅ All services initialized (stubs)")

    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        raise


async def init_real_time_services() -> None:
    """🔥 Инициализировать сервисы реального времени"""
    print("⚡ Initializing real-time services...")
    # Будет реализовано в блоке real-time сервисов
    pass


async def shutdown_services() -> None:
    """Корректно завершить работу всех сервисов"""
    print("🛑 Starting graceful shutdown...")
    # Будет реализовано в следующих блоках
    pass


async def check_connections() -> bool:
    """Проверить подключения к БД и Redis"""
    print("🔍 Checking connections...")

    try:
        # Проверка БД
        from src.data.database import test_connection as test_db
        db_ok = await test_db()
        print(f"📊 Database: {'✅ OK' if db_ok else '❌ Failed'}")

        # Проверка Redis
        from src.data.redis_client import test_connection as test_redis
        redis_ok = await test_redis()
        print(f"🗄️ Redis: {'✅ OK' if redis_ok else '❌ Failed'}")

        return db_ok and redis_ok
    except Exception as e:
        print(f"❌ Connection check failed: {e}")
        return False


async def check_real_time_performance() -> dict:
    """🔥 Проверить производительность системы реального времени"""
    print("📈 Checking real-time performance...")
    # Будет реализовано в блоке real-time сервисов
    return {"real_time_enabled": True, "status": "TODO"}


async def main() -> None:
    """Главная функция запуска приложения"""
    try:
        print("🚀 Starting CryptoBot v3.0 with Real-Time Processing")

        # Настройка обработчиков сигналов
        setup_signal_handlers()

        # Валидация конфигурации
        validate_application_config()

        # Создание бота и диспетчера
        global bot, dp
        bot = await create_bot()
        dp = await setup_dispatcher(bot)

        # Инициализация всех сервисов
        await init_services()

        # Проверка подключений
        connections_ok = await check_connections()
        if not connections_ok:
            raise RuntimeError("Не удалось установить подключения к внешним сервисам")

        print("🎯 Starting bot polling...")

        # Запуск бота
        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("🛑 Received shutdown signal")

    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Critical error in main: {e}")
        raise
    finally:
        # Корректное завершение работы
        await shutdown_services()


if __name__ == "__main__":
    """Точка входа приложения"""
    try:
        print("🎬 Starting CryptoBot application...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Critical error: {e}")
