# 🤖 CryptoBot v3.0 - Real-Time Trading Signals

> Telegram бот для мониторинга криптовалютных торговых пар с автоматической генерацией торговых сигналов на основе технических индикаторов RSI и EMA в **РЕАЛЬНОМ ВРЕМЕНИ**.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Real-Time](https://img.shields.io/badge/real--time-%3C1000ms-red)

## 🎯 Ключевые особенности

- ⚡ **Реальное время**: Обработка данных < 1 секунды
- 📊 **Технические индикаторы**: RSI, EMA с инкрементальными алгоритмами
- 🚨 **Умные сигналы**: Автоматическая генерация торговых сигналов
- 🔧 **Гибкие настройки**: Управление парами и таймфреймами
- 📱 **Telegram интерфейс**: Удобное взаимодействие через бота
- 🏗️ **Масштабируемость**: Поддержка тысяч пользователей

## 🚀 Целевые показатели производительности

| Операция | Целевое время | Статус |
|----------|---------------|--------|
| WebSocket → Обработка | < 10ms | ⚡ |
| RSI расчет | < 100ms | 📊 |
| EMA расчет | < 50ms | 📈 |
| Генерация сигналов | < 200ms | 🚨 |
| Отправка уведомлений | < 500ms | 📱 |
| **ОБЩЕЕ ВРЕМЯ** | **< 1000ms** | **🎯** |

## 🛠️ Технологический стек

- **Python 3.11+** - Основной язык
- **aiogram 3.x** - Telegram Bot Framework
- **PostgreSQL 15+** - База данных
- **Redis 7+** - Кеширование и FSM
- **WebSockets** - Binance API в реальном времени
- **Docker** - Контейнеризация
- **SQLAlchemy 2.x** - Асинхронная ORM

## 📦 Быстрый старт

### 1. Клонирование и настройка
```bash
git clone <repository>
cd crypto_bot

# Создание .env файла
cp .env.example .env
# Отредактируйте .env с вашими настройками
```

### 2. Запуск с Docker
```bash
docker-compose up -d --build
```

### 3. Запуск для разработки
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск PostgreSQL и Redis
docker-compose up -d postgres redis

# Запуск бота
python -m src.main
```

## ⚙️ Конфигурация

### Основные переменные окружения

```bash
# Telegram
BOT_TOKEN=your_bot_token_here

# База данных
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/crypto_bot

# Redis
REDIS_URL=redis://localhost:6379/0

# 🔥 Реальное время
REAL_TIME_ENABLED=true
TARGET_TOTAL_PROCESSING_MS=1000
PERFORMANCE_MONITORING_ENABLED=true
```

## 📊 Архитектура

```
┌─────────────────┐
│   Bot Layer     │ ← Telegram интерфейс
├─────────────────┤
│ Services Layer  │ ← Бизнес логика + Real-Time
├─────────────────┤
│   Data Layer    │ ← Модели, репозитории, кеш
├─────────────────┤
│  Utils Layer    │ ← Утилиты и константы
└─────────────────┘
```

### 🔥 Система реального времени

```
WebSocket → Real-Time Processor → Indicators → Signals → Notifications
    ↓            ↓                     ↓         ↓          ↓
  < 10ms       < 50ms               < 100ms   < 200ms    < 500ms
```

## 🎮 Команды бота

- `/start` - Начать работу с ботом
- **➕ Добавить пару** - Добавить новую торговую пару
- **📊 Мои пары** - Управление существующими парами
- **❌ Удалить пару** - Удалить пару из отслеживания

## 📈 Поддерживаемые индикаторы

### RSI (Relative Strength Index)
- **Периоды**: 14, 21, 30
- **Зоны**: Перепроданность (<30), Перекупленность (>70)
- **Сигналы**: Вход/выход из зон

### EMA (Exponential Moving Average)
- **Периоды**: 20, 50, 100, 200
- **Сигналы**: Пересечения скользящих средних
- **Тренды**: Определение направления движения

## 🔧 Разработка

### Структура проекта
```
src/
├── bot/                    # Telegram бот
│   ├── handlers/          # Обработчики команд
│   ├── keyboards/         # Клавиатуры
│   └── middlewares/       # Middleware
├── services/              # Бизнес логика
│   ├── websocket/        # WebSocket клиенты
│   ├── indicators/       # Расчет индикаторов
│   ├── signals/          # Генерация сигналов
│   ├── notifications/    # Уведомления
│   ├── cache/           # Кеширование
│   └── real_time/       # 🔥 Реальное время
├── data/                 # Работа с данными
│   ├── models/          # SQLAlchemy модели
│   └── repositories/    # Репозитории
├── config/              # Конфигурация
└── utils/               # Утилиты
```

### Тестирование
```bash
# Запуск всех тестов
pytest

# Тестирование производительности
pytest tests/performance/

# Тестирование реального времени
pytest tests/real_time/
```

## 📊 Мониторинг

### Графана дашборд
Доступен по адресу: http://localhost:3000
- Логин: admin
- Пароль: admin

### Метрики производительности
- Время обработки WebSocket сообщений
- Скорость расчета индикаторов
- Latency уведомлений
- Статистика сигналов

## 🐛 Устранение неполадок

### Частые проблемы

1. **Бот не отвечает**
   ```bash
   # Проверить логи
   docker-compose logs app
   ```

2. **Медленная обработка**
   ```bash
   # Проверить производительность
   docker-compose logs app | grep "Performance"
   ```

3. **Ошибки WebSocket**
   ```bash
   # Перезапуск сервисов
   docker-compose restart app
   ```

## 📝 Лицензия

MIT License - см. файл LICENSE

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📞 Поддержка

- 📧 Email: support@cryptobot.com
- 💬 Telegram: @cryptobot_support
- 📖 Документация: docs/

---

**🚀 CryptoBot v3.0 - Торгуйте с умом в реальном времени!**
