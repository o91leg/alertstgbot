# AGENT.MD - Детальная карта всех файлов проекта крипто-бота

> **Версия:** 3.0 ДЕТАЛЬНАЯ + РЕАЛЬНОЕ ВРЕМЯ  
> **Дата создания:** 2025-07-31  
> **Назначение:** Полная детализация каждого файла со всеми функциями и методами для идеальной навигации кодекса Claude + требования реального времени

## 📋 СОДЕРЖАНИЕ

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Требования реального времени](#требования-реального-времени)
3. [Главные файлы](#главные-файлы)
4. [Bot Layer - Telegram интерфейс](#bot-layer---telegram-интерфейс)
5. [Data Layer - Работа с данными](#data-layer---работа-с-данными)
6. [Services Layer - Бизнес логика](#services-layer---бизнес-логика)
7. [Utils Layer - Утилиты](#utils-layer---утилиты)
8. [Config Layer - Конфигурация](#config-layer---конфигурация)
9. [Вспомогательные файлы](#вспомогательные-файлы)
10. [Быстрый поиск по функциям](#быстрый-поиск-по-функциям)

---

## 🏗️ ОБЗОР АРХИТЕКТУРЫ

**Структура проекта:**
```
crypto_bot/
├── src/main.py                 # 🚀 Точка входа
├── .env/.env.example          # 🔧 Переменные окружения
├── docker-compose.yml         # 🐳 Docker конфигурация
├── requirements.txt           # 📦 Python зависимости
├── scripts/                   # 📜 Скрипты
└── src/                       # 💻 Исходный код
    ├── bot/                   # 🤖 Telegram бот
    ├── config/                # ⚙️ Конфигурация
    ├── data/                  # 🗄️ Модели и БД
    ├── services/              # 🔧 Бизнес логика
    └── utils/                 # 🛠️ Утилиты
```

---

## ⚡ ТРЕБОВАНИЯ РЕАЛЬНОГО ВРЕМЕНИ

### 🎯 КРИТИЧЕСКИЕ ТРЕБОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ

**Все технические индикаторы ДОЛЖНЫ рассчитываться в реальном времени:**

#### RSI в реальном времени:
- ✅ Инкрементальный алгоритм расчета без полного пересчета
- ✅ Обновление при каждом WebSocket tick'е
- ✅ Максимальная задержка: **< 100ms**
- ✅ Использование скользящих средних для gains/losses

#### EMA в реальном времени:
- ✅ Формула: `EMA_новая = (Цена_текущая × K) + (EMA_предыдущая × (1-K))`
- ✅ Коэффициент K = 2/(период+1)
- ✅ Обновление всех периодов одновременно
- ✅ Максимальная задержка: **< 50ms**

#### Дополнительные индикаторы:
- ✅ Volume change - реальное время
- ✅ Price change percentage - мгновенно
- ✅ Все индикаторы синхронно

### 📊 АРХИТЕКТУРА РЕАЛЬНОГО ВРЕМЕНИ

```
WebSocket Data → Real-time Processor → Indicator Calculators → Signal Generator → Notifications
      ↓                ↓                        ↓                    ↓              ↓
   < 10ms           < 50ms                  < 100ms              < 200ms        < 500ms
```

**Целевые показатели производительности:**
- **WebSocket → Обработка:** < 10ms
- **Расчет RSI:** < 100ms
- **Расчет EMA:** < 50ms
- **Генерация сигнала:** < 200ms
- **Отправка уведомления:** < 500ms
- **🎯 ОБЩЕЕ ВРЕМЯ: < 1 СЕКУНДЫ**

---

# 📁 ДЕТАЛЬНАЯ КАРТА ВСЕХ ФАЙЛОВ

## 🚀 ГЛАВНЫЕ ФАЙЛЫ

### 📄 `src/main.py`
**Назначение:** Главная точка входа приложения - запуск и инициализация всех сервисов с поддержкой реального времени

**Глобальные переменные:**
- `bot: Optional[Bot]` - Экземпляр Telegram бота
- `dp: Optional[Dispatcher]` - Диспетчер aiogram
- `stream_manager: Optional[StreamManager]` - Менеджер WebSocket потоков **для реального времени**
- `telegram_sender: Optional[TelegramSender]` - Отправщик уведомлений
- `real_time_processor: Optional[RealTimeProcessor]` - **НОВЫЙ: Процессор реального времени**
- `performance_monitor: Optional[PerformanceMonitor]` - **НОВЫЙ: Монитор производительности**
- `logger` - Структурированный логгер

**Все функции:**
```python
async def create_bot() -> Bot
    """Создать и настроить экземпляр Telegram бота"""

async def setup_dispatcher() -> Dispatcher
    """Настроить диспетчер и зарегистрировать все обработчики"""

def validate_application_config() -> None
    """Валидировать конфигурацию всего приложения + настройки реального времени"""

def setup_signal_handlers() -> None
    """Настроить обработчики системных сигналов (SIGINT, SIGTERM)"""

async def init_services() -> None
    """Инициализировать все сервисы: БД, Redis, WebSocket, уведомления + реальное время"""

async def init_real_time_services() -> None
    """🔥 НОВАЯ: Инициализировать сервисы реального времени"""

async def shutdown_services() -> None
    """Корректно завершить работу всех сервисов"""

async def check_connections() -> bool
    """Проверить подключения к БД и Redis"""

async def check_real_time_performance() -> Dict[str, float]
    """🔥 НОВАЯ: Проверить производительность системы реального времени"""

async def main() -> None
    """Главная функция запуска приложения"""
```

---

## 🤖 BOT LAYER - TELEGRAM ИНТЕРФЕЙС

### 📂 `src/bot/handlers/`

#### 📄 `src/bot/handlers/start_handler.py`
**Назначение:** Обработка команды /start и регистрация новых пользователей

**Функции:**
```python
@start_router.message(CommandStart())
async def handle_start_command(message: Message, session: AsyncSession, state: FSMContext)
    """Обработчик команды /start с регистрацией пользователя"""

async def get_or_create_user(session: AsyncSession, telegram_user: Any) -> User
    """Получить существующего или создать нового пользователя"""

async def setup_default_pair_for_user(session: AsyncSession, user_id: int) -> bool
    """Создать дефолтную пару BTCUSDT для нового пользователя + подключить к реальному времени"""

async def initialize_real_time_monitoring(user_id: int, symbol: str) -> bool
    """🔥 НОВАЯ: Инициализировать мониторинг реального времени для пользователя"""

def create_welcome_message(display_name: str) -> str
    """Создать приветственное сообщение для нового пользователя"""

def create_welcome_back_message(display_name: str) -> str
    """Создать сообщение для возвращающегося пользователя"""

def register_start_handlers(dp: Dispatcher) -> None
    """Зарегистрировать обработчики команды /start в диспетчере"""
```

**Роутер:** `start_router = Router()`

---

#### 📄 `src/bot/handlers/remove_pair_handler.py`
**Назначение:** Обработка удаления торговых пар из отслеживания

**FSM состояния:**
```python
class RemovePairStates(StatesGroup):
    selecting_pair = State()      # Выбор пары для удаления
    confirming_removal = State()  # Подтверждение удаления
```

**Функции:**
```python
@remove_pair_router.callback_query(F.data == "remove_pair")
async def handle_remove_pair_start(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Начать процесс удаления торговой пары"""

@remove_pair_router.callback_query(RemovePairStates.selecting_pair)
async def handle_pair_selection_for_removal(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Обработать выбор пары для удаления"""

@remove_pair_router.callback_query(RemovePairStates.confirming_removal)
async def handle_removal_confirmation(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Обработать подтверждение удаления пары"""

async def get_user_pairs_for_removal(session: AsyncSession, user_id: int) -> List[UserPair]
    """Получить список пар пользователя для удаления"""

def create_pairs_removal_keyboard(user_pairs: List[UserPair]) -> InlineKeyboardMarkup
    """Создать клавиатуру выбора пары для удаления"""

def create_removal_confirmation_message(pair: Pair) -> str
    """Создать сообщение подтверждения удаления пары"""

async def execute_pair_removal(session: AsyncSession, user_id: int, pair_id: int) -> bool
    """Выполнить удаление пары из отслеживания пользователя + остановить реальное время"""

async def stop_real_time_monitoring(user_id: int, symbol: str) -> bool
    """🔥 НОВАЯ: Остановить мониторинг реального времени для пары"""

def register_remove_pair_handlers(dp: Dispatcher) -> None
    """Зарегистрировать обработчики удаления пар"""
```

**Роутер:** `remove_pair_router = Router()`

---

### 📂 `src/bot/handlers/add_pair/` (Модуль)

#### 📄 `src/bot/handlers/add_pair/add_pair_handler.py`
**Назначение:** Основные FSM обработчики для добавления торговых пар

**FSM состояния:**
```python
class AddPairStates(StatesGroup):
    waiting_for_symbol = State()  # Ожидание ввода символа пары
    confirming_pair = State()     # Подтверждение добавления пары
```

**Функции:**
```python
@add_pair_router.callback_query(F.data == "add_pair")
async def handle_add_pair_start(callback: CallbackQuery, state: FSMContext)
    """Начать процесс добавления новой торговой пары"""

@add_pair_router.message(AddPairStates.waiting_for_symbol)
async def handle_pair_symbol_input(message: Message, session: AsyncSession, state: FSMContext)
    """Обработать ввод символа торговой пары пользователем"""

@add_pair_router.callback_query(AddPairStates.confirming_pair, F.data == "confirm_add_pair")
async def handle_pair_confirmation(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Обработать подтверждение добавления пары + запустить реальное время"""

@add_pair_router.callback_query(F.data == "cancel_add_pair")
async def handle_cancel_add_pair(callback: CallbackQuery, state: FSMContext)
    """Отменить процесс добавления пары"""

def register_add_pair_handlers(dp: Dispatcher) -> None
    """Зарегистрировать обработчики добавления пар в диспетчере"""
```

**Роутер:** `add_pair_router = Router()`

#### 📄 `src/bot/handlers/add_pair/add_pair_logic.py`
**Назначение:** Бизнес-логика добавления пар с поддержкой реального времени

**Функции:**
```python
async def process_symbol_input(session: AsyncSession, symbol: str) -> Dict[str, Any]
    """Обработать и валидировать введенный символ торговой пары"""

async def validate_pair_on_binance(symbol: str) -> Dict[str, Any]
    """Валидировать существование пары на Binance через API"""

async def execute_add_pair(session: AsyncSession, user_id: int, symbol: str) -> Dict[str, Any]
    """Выполнить добавление пары в БД и настройки пользователя"""

async def setup_pair_timeframes(session: AsyncSession, user_id: int, pair_id: int) -> Dict[str, bool]
    """Настроить дефолтные таймфреймы для добавленной пары"""

async def fetch_initial_candle_data(symbol: str) -> bool
    """Загрузить начальные исторические данные для новой пары"""

async def initialize_real_time_indicators(symbol: str, timeframes: List[str]) -> bool
    """🔥 НОВАЯ: Инициализировать индикаторы реального времени для новой пары"""

async def start_websocket_monitoring(symbol: str) -> bool
    """🔥 НОВАЯ: Запустить WebSocket мониторинг для пары"""

async def precompute_initial_indicators(symbol: str, timeframes: List[str]) -> Dict[str, Dict[str, float]]
    """🔥 НОВАЯ: Предварительно рассчитать индикаторы для быстрого старта"""
```

#### 📄 `src/bot/handlers/add_pair/add_pair_formatters.py`
**Назначение:** Форматирование сообщений для добавления пар

**Функции:**
```python
def create_add_pair_instruction() -> str
    """Создать инструкцию для пользователя о вводе символа пары"""

def create_pair_confirmation_text(symbol: str, pair_info: Dict[str, Any]) -> str
    """Создать текст подтверждения с информацией о паре + уведомление о реальном времени"""

def create_pair_error_text(error_type: str, symbol: str = None) -> str
    """Создать сообщение об ошибке при добавлении пары"""

def create_pair_added_text(symbol: str, timeframes_count: int) -> str
    """Создать сообщение об успешном добавлении пары + старт мониторинга"""

def create_add_error_text(error_message: str) -> str
    """Создать сообщение об общей ошибке при добавлении"""

def format_pair_info_display(pair_info: Dict[str, Any]) -> str
    """Форматировать информацию о паре для отображения"""

def create_real_time_status_text(symbol: str, is_active: bool) -> str
    """🔥 НОВАЯ: Создать текст статуса мониторинга реального времени"""
```

---

### 📂 `src/bot/handlers/my_pairs/` (Модуль)

#### 📄 `src/bot/handlers/my_pairs/my_pairs_handler.py`
**Назначение:** Основные обработчики FSM для управления торговыми парами пользователя

**FSM состояния:**
```python
class MyPairsStates(StatesGroup):
    viewing_pairs = State()        # Просмотр списка пар
    managing_timeframes = State()  # Управление таймфреймами
    viewing_rsi = State()          # Просмотр RSI значений
    viewing_real_time_status = State()  # 🔥 НОВОЕ: Просмотр статуса реального времени
```

**Функции:**
```python
@my_pairs_router.callback_query(F.data == "my_pairs")
async def handle_my_pairs_start(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Показать список пар пользователя"""

@my_pairs_router.callback_query(MyPairsStates.viewing_pairs)
async def handle_pair_management(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Обработать выбор пары для управления"""

@my_pairs_router.callback_query(MyPairsStates.managing_timeframes)
async def handle_timeframe_toggle(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Переключить состояние таймфрейма для пары + обновить реальное время"""

@my_pairs_router.callback_query(MyPairsStates.viewing_rsi)
async def handle_rsi_view(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """Показать текущие значения RSI для пары В РЕАЛЬНОМ ВРЕМЕНИ"""

@my_pairs_router.callback_query(MyPairsStates.viewing_real_time_status)
async def handle_real_time_status_view(callback: CallbackQuery, session: AsyncSession, state: FSMContext)
    """🔥 НОВАЯ: Показать статус мониторинга реального времени"""

async def get_user_pairs_with_stats(session: AsyncSession, user_id: int) -> List[Dict[str, Any]]
    """Получить пары пользователя со статистикой сигналов"""

async def get_real_time_performance_stats(user_id: int, symbol: str) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику производительности реального времени"""

def register_my_pairs_handlers(dp: Dispatcher) -> None
    """Зарегистрировать обработчики управления парами"""
```

**Роутер:** `my_pairs_router = Router()`

#### 📄 `src/bot/handlers/my_pairs/my_pairs_formatters.py`
**Назначение:** Форматирование сообщений для управления парами

**Функции:**
```python
def create_no_pairs_message() -> str
    """Создать сообщение когда у пользователя нет пар"""

def create_pairs_list_message(user_pairs: List[Dict[str, Any]]) -> str
    """Форматировать сообщение со списком пар пользователя + статус реального времени"""

def create_pair_management_message(pair: Pair, user_pair: UserPair) -> str
    """Создать сообщение управления конкретной парой"""

def create_rsi_display_message(symbol: str, rsi_data: Dict[str, float], last_update_time: datetime) -> str
    """🔥 ОБНОВЛЕНА: Создать сообщение с отображением RSI значений + время последнего обновления"""

def create_rsi_error_message(symbol: str, error: str) -> str
    """Создать сообщение об ошибке получения RSI"""

def format_timeframes_status(timeframes: Dict[str, bool]) -> str
    """Форматировать статус включенных/выключенных таймфреймов"""

def format_pair_statistics(signals_count: int, last_signal: Optional[datetime]) -> str
    """Форматировать статистику по паре (сигналы, последний сигнал)"""

def create_real_time_performance_message(symbol: str, performance_stats: Dict[str, Any]) -> str
    """🔥 НОВАЯ: Создать сообщение с производительностью реального времени"""

def format_real_time_indicators(symbol: str, indicators: Dict[str, Dict[str, float]], timestamps: Dict[str, datetime]) -> str
    """🔥 НОВАЯ: Форматировать индикаторы реального времени с временными метками"""
```

#### 📄 `src/bot/handlers/my_pairs/my_pairs_keyboards.py`
**Назначение:** Клавиатуры для управления парами

**Функции:**
```python
def create_no_pairs_keyboard() -> InlineKeyboardMarkup
    """Создать клавиатуру когда у пользователя нет пар"""

def create_pairs_list_keyboard(user_pairs: List[Dict[str, Any]]) -> InlineKeyboardMarkup
    """Создать клавиатуру со списком пар для выбора"""

def create_pair_management_keyboard(pair_id: int, user_pair: UserPair) -> InlineKeyboardMarkup
    """Создать клавиатуру управления конкретной парой + кнопка реального времени"""

def create_timeframes_keyboard(pair_id: int, timeframes: Dict[str, bool]) -> InlineKeyboardMarkup
    """Создать клавиатуру переключения таймфреймов"""

def create_rsi_display_keyboard(pair_id: int) -> InlineKeyboardMarkup
    """Создать клавиатуру для просмотра RSI значений + обновить"""

def create_real_time_status_keyboard(pair_id: int, is_monitoring: bool) -> InlineKeyboardMarkup
    """🔥 НОВАЯ: Создать клавиатуру статуса реального времени"""

def get_back_to_management_keyboard(pair_id: int) -> InlineKeyboardMarkup
    """Создать клавиатуру возврата к управлению парой"""
```

#### 📄 `src/bot/handlers/my_pairs/my_pairs_logic.py`
**Назначение:** Бизнес-логика управления парами

**Функции:**
```python
async def calculate_rsi_for_pair(session: AsyncSession, symbol: str, timeframes: List[str]) -> Dict[str, float]
    """🔥 ОБНОВЛЕНА: Получить текущие значения RSI В РЕАЛЬНОМ ВРЕМЕНИ"""

async def get_real_time_rsi_values(symbol: str, timeframes: List[str]) -> Dict[str, Tuple[float, datetime]]
    """🔥 НОВАЯ: Получить RSI из кеша реального времени с временными метками"""

async def toggle_timeframe(session: AsyncSession, user_id: int, pair_id: int, timeframe: str) -> bool
    """Переключить состояние таймфрейма (включен/выключен) + обновить мониторинг"""

async def get_pair_signal_statistics(session: AsyncSession, user_id: int, pair_id: int) -> Dict[str, Any]
    """Получить статистику сигналов по паре для пользователя"""

async def update_timeframes_config(session: AsyncSession, user_id: int, pair_id: int, new_config: Dict[str, bool]) -> bool
    """Обновить конфигурацию таймфреймов для пары + перенастроить реальное время"""

async def validate_timeframe_change(current_config: Dict[str, bool], timeframe: str, new_state: bool) -> bool
    """Валидировать изменение таймфрейма (минимум один должен быть включен)"""

async def get_real_time_monitoring_status(symbol: str) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статус мониторинга реального времени"""

async def restart_real_time_monitoring(symbol: str, timeframes: List[str]) -> bool
    """🔥 НОВАЯ: Перезапустить мониторинг реального времени при изменении настроек"""
```

---

### 📂 `src/bot/keyboards/`

#### 📄 `src/bot/keyboards/main_menu_kb.py`
**Назначение:** Все клавиатуры для навигации по боту

**Функции:**
```python
def get_main_menu_keyboard() -> InlineKeyboardMarkup
    """Создать главное меню бота с основными функциями + статус реального времени"""

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup
    """Создать клавиатуру с кнопкой возврата в главное меню"""

def get_confirmation_keyboard(action: str, item_id: str = None) -> InlineKeyboardMarkup
    """Создать клавиатуру подтверждения действия (Да/Нет)"""

def get_loading_keyboard() -> InlineKeyboardMarkup
    """Создать клавиатуру с индикатором загрузки"""

def get_menu_with_notification_button(show_notification_controls: bool = True) -> InlineKeyboardMarkup
    """Создать расширенное меню с управлением уведомлениями"""

def get_navigation_keyboard(back_callback: str = "main_menu", additional_buttons: list = None) -> InlineKeyboardMarkup
    """Создать универсальную навигационную клавиатуру"""

def get_error_keyboard() -> InlineKeyboardMarkup
    """Создать клавиатуру для сообщений об ошибках"""

def get_settings_keyboard() -> InlineKeyboardMarkup
    """Создать клавиатуру настроек бота + настройки реального времени"""

def get_help_keyboard() -> InlineKeyboardMarkup
    """Создать клавиатуру раздела помощи"""

def get_real_time_controls_keyboard() -> InlineKeyboardMarkup
    """🔥 НОВАЯ: Создать клавиатуру управления реальным временем"""
```

---

### 📂 `src/bot/middlewares/`

#### 📄 `src/bot/middlewares/database_mw.py`
**Назначение:** Middleware для автоматического создания сессий БД

**Классы и функции:**
```python
class DatabaseMiddleware(BaseMiddleware):
    """Middleware для предоставления сессии БД в обработчики"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Основной метод middleware - создание и управление сессией БД"""

    async def _handle_database_error(
        self,
        event: TelegramObject,
        error: Exception,
        user_id: Optional[int] = None
    ) -> None:
        """Обработать ошибку базы данных и отправить сообщение пользователю"""

    def _extract_user_id(self, event: TelegramObject) -> Optional[int]
        """Извлечь ID пользователя из события"""

    def _create_error_message(self, error: Exception) -> str
        """Создать пользовательское сообщение об ошибке"""
```

---

## 🗄️ DATA LAYER - РАБОТА С ДАННЫМИ

### 📂 `src/data/models/`

#### 📄 `src/data/models/base_model.py`
**Назначение:** Базовая модель для всех таблиц

**Классы:**
```python
class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy моделей"""
    
    # Автоматические поля для всех моделей
    created_at: Mapped[datetime]  # Время создания
    updated_at: Mapped[datetime]  # Время обновления
```

#### 📄 `src/data/models/user_model.py`
**Назначение:** Модель пользователя Telegram

**Модель:**
```python
class User(Base):
    """Модель пользователя Telegram"""
    
    # Поля таблицы
    id: BigInteger                      # Telegram user ID (PK)
    username: String(50)                # @username
    first_name: String(100)             # Имя
    last_name: String(100)              # Фамилия  
    language_code: String(10)           # Код языка
    notifications_enabled: Boolean      # Включены ли уведомления
    is_active: Boolean                  # Активен ли пользователь
    is_blocked: Boolean                 # Заблокирован ли бот
    total_signals_received: Integer     # Всего получено сигналов
    real_time_enabled: Boolean          # 🔥 НОВОЕ: Включен ли мониторинг реального времени
    real_time_performance_stats: JSON   # 🔥 НОВОЕ: Статистика производительности
    
    # Связи
    user_pairs: relationship("UserPair")
    signal_history: relationship("SignalHistory")
```

**Методы:**
```python
@property
def display_name(self) -> str
    """Получить отображаемое имя пользователя"""

def update_from_telegram(self, telegram_user) -> None
    """Обновить данные пользователя из Telegram"""

def increment_signals_count(self) -> None
    """Увеличить счетчик полученных сигналов"""

def toggle_notifications(self) -> bool
    """Переключить состояние уведомлений"""

def mark_as_blocked(self) -> None
    """Отметить пользователя как заблокировавшего бота"""

def mark_as_active(self) -> None
    """Отметить пользователя как активного"""

def enable_real_time_monitoring(self) -> None
    """🔥 НОВАЯ: Включить мониторинг реального времени"""

def disable_real_time_monitoring(self) -> None
    """🔥 НОВАЯ: Выключить мониторинг реального времени"""

def update_performance_stats(self, stats: Dict[str, Any]) -> None
    """🔥 НОВАЯ: Обновить статистику производительности"""

def to_dict(self) -> Dict[str, Any]
    """Преобразовать модель в словарь"""
```## 🔧 SERVICES LAYER - БИЗНЕС ЛОГИКА

### 📂 `src/services/real_time/` 🔥 НОВЫЙ МОДУЛЬ

#### 📄 `src/services/real_time/real_time_processor.py` 🔥 НОВЫЙ ФАЙЛ
**Назначение:** Главный процессор данных реального времени

**Класс:**
```python
class RealTimeProcessor(LoggerMixin):
    """Главный процессор данных реального времени"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация процессора реального времени"""

async def start(self) -> bool
    """Запустить процессор реального времени"""

async def stop(self) -> None
    """Остановить процессор реального времени"""

async def process_websocket_data(self, symbol: str, timeframe: str, price_data: Dict[str, Any]) -> Dict[str, Any]
    """🎯 ОСНОВНАЯ ФУНКЦИЯ: Обработать данные WebSocket в реальном времени"""

async def _calculate_indicators_real_time(self, symbol: str, timeframe: str, price: float) -> Dict[str, Any]
    """Рассчитать все индикаторы в реальном времени"""

async def _update_rsi_real_time(self, symbol: str, timeframe: str, price: float) -> Tuple[float, int]
    """Обновить RSI в реальном времени (возвращает значение + время обработки)"""

async def _update_ema_real_time(self, symbol: str, timeframe: str, price: float) -> Dict[int, Tuple[float, int]]
    """Обновить все EMA в реальном времени"""

async def _check_signal_conditions(self, symbol: str, timeframe: str, indicators: Dict[str, Any]) -> List[Dict[str, Any]]
    """Проверить условия сигналов в реальном времени"""

async def _generate_real_time_notifications(self, signals: List[Dict[str, Any]]) -> int
    """Генерировать уведомления в реальном времени"""

def get_processing_performance_stats(self) -> Dict[str, Any]
    """Получить статистику производительности"""

def get_real_time_status(self) -> Dict[str, Any]
    """Получить статус системы реального времени"""

async def validate_performance_targets(self) -> Dict[str, bool]
    """Проверить соответствие целевым показателям производительности"""
```

**Глобальный экземпляр:** `real_time_processor = RealTimeProcessor()`

#### 📄 `src/services/real_time/performance_monitor.py` 🔥 НОВЫЙ ФАЙЛ
**Назначение:** Мониторинг производительности реального времени

**Класс:**
```python
class PerformanceMonitor:
    """Монитор производительности реального времени"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация монитора производительности"""

def start_timing(self, operation_id: str) -> str
    """Начать замер времени операции"""

def end_timing(self, timing_id: str) -> int
    """Закончить замер времени (возвращает время в мс)"""

def record_processing_time(self, operation_type: str, time_ms: int) -> None
    """Записать время обработки"""

def get_average_processing_time(self, operation_type: str, window_minutes: int = 5) -> float
    """Получить среднее время обработки"""

def check_performance_targets(self) -> Dict[str, bool]
    """Проверить соответствие целевым показателям"""

def get_performance_report(self) -> Dict[str, Any]
    """Получить отчет о производительности"""

def get_bottlenecks(self) -> List[Dict[str, Any]]
    """Определить узкие места в производительности"""

async def alert_on_performance_degradation(self) -> None
    """Отправить уведомление о снижении производительности"""
```

**Глобальный экземпляр:** `performance_monitor = PerformanceMonitor()`

### 📂 `src/services/websocket/`

#### 📄 `src/services/websocket/binance_websocket.py`
**Назначение:** WebSocket клиент для Binance API

**Перечисления:**
```python
class ConnectionState(Enum):
    """Состояния WebSocket соединения"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    CLOSED = "closed"
```

**Класс:**
```python
class BinanceWebSocketClient(LoggerMixin):
    """WebSocket клиент для Binance"""
```

**Методы:**
```python
def __init__(self, message_handler: Optional[Callable] = None, error_handler: Optional[Callable] = None)
    """Инициализация клиента"""

async def connect(self) -> bool
    """Подключиться к WebSocket серверу"""

async def disconnect(self) -> None
    """Отключиться от WebSocket сервера"""

async def subscribe_to_streams(self, streams: List[str]) -> bool
    """Подписаться на потоки данных"""

async def unsubscribe_from_streams(self, streams: List[str]) -> bool
    """Отписаться от потоков данных"""

async def send_ping(self) -> bool
    """Отправить ping сообщение"""

async def handle_message(self, message: str) -> None
    """🔥 ОБНОВЛЕНА: Обработать входящее сообщение + передать в реальное время"""

async def handle_error(self, error: Exception) -> None
    """Обработать ошибку подключения"""

async def reconnect(self) -> bool
    """Переподключиться при разрыве соединения"""

async def start_ping_task(self) -> None
    """Запустить задачу отправки ping"""

async def stop_ping_task(self) -> None
    """Остановить задачу отправки ping"""

def get_connection_state(self) -> ConnectionState
    """Получить текущее состояние подключения"""

def is_connected(self) -> bool
    """Проверить подключен ли клиент"""

async def close(self) -> None
    """Закрыть соединение и очистить ресурсы"""

async def enable_real_time_processing(self) -> None
    """🔥 НОВАЯ: Включить обработку реального времени"""

def get_message_processing_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику обработки сообщений"""
```

#### 📄 `src/services/websocket/stream_manager.py`
**Назначение:** Управление потоками WebSocket данных

**Вспомогательные функции:**
```python
def get_kline_stream_name(symbol: str, timeframe: str) -> str
    """Получить имя потока для kline данных"""

def get_ticker_stream_name(symbol: str) -> str
    """Получить имя потока для ticker данных"""

def get_depth_stream_name(symbol: str, level: str = "5") -> str
    """Получить имя потока для depth данных"""

def parse_stream_name(stream_name: str) -> dict
    """Разобрать имя потока на компоненты"""
```

**Класс:**
```python
class StreamManager:
    """Менеджер WebSocket потоков"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация менеджера потоков"""

async def start(self) -> bool
    """Запустить менеджер потоков"""

async def stop(self) -> None
    """Остановить менеджер потоков"""

async def add_symbol_stream(self, symbol: str, timeframes: List[str]) -> bool
    """Добавить потоки для символа"""

async def remove_symbol_stream(self, symbol: str) -> bool
    """Удалить потоки для символа"""

async def update_subscriptions(self) -> bool
    """Обновить подписки на основе активных пользователей"""

async def get_active_streams(self) -> List[str]
    """Получить список активных потоков"""

async def get_required_streams(self) -> List[str]
    """Получить список необходимых потоков из БД"""

async def handle_websocket_message(self, message: Dict[str, Any]) -> None
    """🔥 ОБНОВЛЕНА: Обработать сообщение от WebSocket + реальное время"""

async def handle_websocket_error(self, error: Exception) -> None
    """Обработать ошибку WebSocket"""

def get_stream_statistics(self) -> Dict[str, Any]
    """Получить статистику потоков"""

def is_running(self) -> bool
    """Проверить работает ли менеджер"""

async def optimize_for_real_time(self) -> None
    """🔥 НОВАЯ: Оптимизировать менеджер для реального времени"""

async def enable_high_frequency_mode(self) -> None
    """🔥 НОВАЯ: Включить режим высокой частоты обновлений"""
```

#### 📄 `src/services/websocket/binance_data_processor.py`
**Назначение:** Обработка данных от Binance WebSocket

**Класс:**
```python
class BinanceDataProcessor:
    """Обработчик данных от Binance WebSocket"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация обработчика"""

async def process_websocket_message(self, message: Dict[str, Any]) -> None
    """🔥 ОБНОВЛЕНА: Обработать сообщение от WebSocket + передать в реальное время"""

async def _process_kline_message(self, stream_name: str, data: Dict[str, Any]) -> None
    """🔥 ОБНОВЛЕНА: Обработать kline сообщение + запустить расчет индикаторов"""

async def _process_ticker_message(self, stream_name: str, data: Dict[str, Any]) -> None
    """Обработать ticker сообщение"""

async def _extract_symbol_timeframe(self, stream_name: str) -> Tuple[str, str]
    """Извлечь символ и таймфрейм из имени потока"""

async def _validate_kline_data(self, data: Dict[str, Any]) -> bool
    """Валидировать kline данные"""

async def _convert_kline_to_candle(self, data: Dict[str, Any]) -> Dict[str, Any]
    """Конвертировать kline данные в формат свечи"""

async def _process_candle_data(self, symbol: str, timeframe: str, candle_data: Dict[str, Any]) -> None
    """🔥 ОБНОВЛЕНА: Обработать данные свечи + запустить реальное время"""

async def _trigger_real_time_processing(self, symbol: str, timeframe: str, price: float) -> None
    """🔥 НОВАЯ: Запустить обработку реального времени"""

def get_processing_stats(self) -> Dict[str, Any]
    """Получить статистику обработки"""

def reset_stats(self) -> None
    """Сбросить статистику доставки"""

def get_real_time_performance(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить производительность реального времени"""
```

### 📂 `src/services/indicators/`

#### 📄 `src/services/indicators/rsi_calculator.py`
**Назначение:** Калькулятор RSI индикатора

**Класс:**
```python
class RSICalculator:
    """🔥 ОБНОВЛЕН: Калькулятор RSI (Relative Strength Index) с поддержкой реального времени"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация калькулятора RSI"""

async def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]
    """Рассчитать RSI для массива цен"""

async def calculate_real_time_rsi(self, symbol: str, timeframe: str, current_price: float, period: int = 14) -> Tuple[Optional[float], int]
    """🔥 ГЛАВНАЯ ФУНКЦИЯ: Рассчитать RSI в реальном времени (возвращает значение + время обработки)"""

async def update_rsi_incremental(self, symbol: str, timeframe: str, new_price: float, period: int = 14) -> Tuple[Optional[float], int]
    """🔥 НОВАЯ: Инкрементальное обновление RSI без полного пересчета"""

def _calculate_rsi_basic(self, prices: List[float], period: int) -> Optional[float]
    """Базовый алгоритм расчета RSI"""

def _calculate_gains_losses(self, prices: List[float]) -> Tuple[List[float], List[float]]
    """Рассчитать прибыли и убытки между ценами"""

def _smooth_values(self, values: List[float], period: int) -> List[float]
    """Сгладить значения используя EMA"""

def _calculate_rs(self, avg_gain: float, avg_loss: float) -> float
    """Рассчитать Relative Strength (RS)"""

def _calculate_rsi_from_rs(self, rs: float) -> float
    """Рассчитать RSI из RS"""

async def _get_cached_rsi_state(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]
    """🔥 НОВАЯ: Получить закешированное состояние RSI для инкрементального обновления"""

async def _save_rsi_state(self, symbol: str, timeframe: str, state: Dict[str, Any]) -> None
    """🔥 НОВАЯ: Сохранить состояние RSI в кеш"""

async def calculate_rsi_for_multiple_periods(self, prices: List[float], periods: List[int]) -> Dict[int, float]
    """Рассчитать RSI для нескольких периодов"""

def validate_rsi_inputs(self, prices: List[float], period: int) -> bool
    """Валидировать входные данные для RSI"""

def get_rsi_signal_strength(self, rsi_value: float) -> str
    """Определить силу сигнала RSI"""

def get_performance_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику производительности"""
```

#### 📄 `src/services/indicators/ema_calculator.py`
**Назначение:** Калькулятор EMA индикатора

**Класс:**
```python
class EMACalculator:
    """🔥 ОБНОВЛЕН: Калькулятор EMA (Exponential Moving Average) с поддержкой реального времени"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация калькулятора EMA"""

async def calculate_ema(self, prices: List[float], period: int) -> Optional[float]
    """Рассчитать EMA для массива цен"""

async def calculate_real_time_ema(self, symbol: str, timeframe: str, current_price: float, period: int) -> Tuple[Optional[float], int]
    """🔥 ГЛАВНАЯ ФУНКЦИЯ: Рассчитать EMA в реальном времени (возвращает значение + время обработки)"""

async def update_ema_incremental(self, symbol: str, timeframe: str, new_price: float, period: int) -> Tuple[Optional[float], int]
    """🔥 НОВАЯ: Инкрементальное обновление EMA используя формулу реального времени"""

async def calculate_multiple_ema_real_time(self, symbol: str, timeframe: str, current_price: float, periods: List[int]) -> Dict[int, Tuple[float, int]]
    """🔥 НОВАЯ: Рассчитать EMA для нескольких периодов одновременно в реальном времени"""

def _calculate_ema_basic(self, prices: List[float], period: int) -> Optional[float]
    """Базовый алгоритм расчета EMA"""

def _calculate_smoothing_factor(self, period: int) -> float
    """Рассчитать коэффициент сглаживания (альфа)"""

def _calculate_initial_sma(self, prices: List[float], period: int) -> float
    """Рассчитать начальное SMA для EMA"""

async def _get_cached_ema_value(self, symbol: str, timeframe: str, period: int) -> Optional[float]
    """🔥 НОВАЯ: Получить закешированное значение EMA"""

async def _save_ema_value(self, symbol: str, timeframe: str, period: int, value: float) -> None
    """🔥 НОВАЯ: Сохранить значение EMA в кеш"""

def detect_ema_crossover(self, ema_short: float, ema_long: float, prev_ema_short: float, prev_ema_long: float) -> Optional[str]
    """Определить пересечение EMA (bullish/bearish)"""

def calculate_ema_slope(self, current_ema: float, previous_ema: float) -> float
    """Рассчитать наклон EMA"""

def validate_ema_inputs(self, prices: List[float], period: int) -> bool
    """Валидировать входные данные для EMA"""

def get_performance_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику производительности"""
```

### 📂 `src/services/signals/`

#### 📄 `src/services/signals/rsi_signals.py`
**Назначение:** Генератор RSI сигналов

**Класс:**
```python
class RSISignalGenerator:
    """🔥 ОБНОВЛЕН: Генератор RSI сигналов с поддержкой реального времени"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация генератора RSI сигналов"""

async def process_rsi_update_real_time(self, session: AsyncSession, symbol: str, timeframe: str, rsi_value: float, price: float, processing_time_ms: int, volume_change_percent: Optional[float] = None) -> int
    """🔥 ГЛАВНАЯ ФУНКЦИЯ: Обработать обновление RSI в реальном времени"""

async def process_rsi_update(self, session: AsyncSession, symbol: str, timeframe: str, rsi_value: float, price: float, volume_change_percent: Optional[float] = None) -> int
    """Обработать обновление RSI и сгенерировать сигналы"""

async def check_rsi_signals_real_time(self, session: AsyncSession, symbol: str, timeframe: str, current_rsi: float, previous_rsi: Optional[float], current_price: float, volume_change_percent: Optional[float] = None) -> List[Dict[str, Any]]
    """🔥 НОВАЯ: Проверить условия RSI сигналов в реальном времени с учетом предыдущего значения"""

async def check_rsi_signals(self, session: AsyncSession, symbol: str, timeframe: str, current_rsi: float, current_price: float, volume_change_percent: Optional[float] = None) -> List[Dict[str, Any]]
    """Проверить условия RSI сигналов"""

async def generate_notifications(self, signals: List[Dict[str, Any]]) -> int
    """Сгенерировать уведомления для RSI сигналов"""

async def generate_real_time_notifications(self, signals: List[Dict[str, Any]], processing_time_ms: int) -> int
    """🔥 НОВАЯ: Генерировать уведомления в реальном времени с метриками"""

def _determine_rsi_signal_type(self, rsi_value: float) -> Optional[str]
    """Определить тип RSI сигнала по значению"""

def _determine_rsi_signal_type_with_trend(self, current_rsi: float, previous_rsi: Optional[float]) -> Optional[str]
    """🔥 НОВАЯ: Определить тип RSI сигнала с учетом тренда"""

async def _get_users_for_notification(self, session: AsyncSession, symbol: str, timeframe: str) -> List[int]
    """Получить пользователей для уведомления"""

async def _can_send_signal(self, session: AsyncSession, user_id: int, symbol: str, timeframe: str, signal_type: str) -> bool
    """Проверить можно ли отправить сигнал (антиспам)"""

async def _save_signal_history(self, session: AsyncSession, signals: List[Dict[str, Any]]) -> None
    """Сохранить историю сигналов в БД"""

async def _save_real_time_signal_history(self, session: AsyncSession, signals: List[Dict[str, Any]], processing_time_ms: int) -> None
    """🔥 НОВАЯ: Сохранить историю сигналов реального времени с метриками"""

def _get_signal_interval(self, signal_type: str) -> int
    """Получить интервал между сигналами для типа"""

def _format_signal_message(self, signal_data: Dict[str, Any]) -> str
    """Форматировать сообщение сигнала"""

async def get_signal_statistics(self) -> Dict[str, Any]
    """Получить статистику генерации сигналов"""

def get_real_time_performance_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику производительности реального времени"""
```

**Глобальный экземпляр:** `rsi_signal_generator = RSISignalGenerator()`

#### 📄 `src/services/signals/signal_aggregator.py`
**Назначение:** Агрегатор всех типов сигналов

**Класс:**
```python
class SignalAggregator:
    """🔥 ОБНОВЛЕН: Агрегатор всех типов сигналов с поддержкой реального времени"""
```

**Методы:**
```python
def __init__(self)
    """Инициализация агрегатора сигналов"""

async def process_candle_update_real_time(self, session: AsyncSession, symbol: str, timeframe: str, candle_data: Dict[str, Any], is_closed: bool = True) -> Dict[str, int]
    """🔥 ГЛАВНАЯ ФУНКЦИЯ: Обработать обновление свечи в реальном времени"""

async def process_candle_update(self, session: AsyncSession, symbol: str, timeframe: str, candle_data: Dict[str, Any], is_closed: bool = True) -> Dict[str, int]
    """Обработать обновление свечи и сгенерировать сигналы"""

async def _calculate_indicators_real_time(self, symbol: str, timeframe: str, candle_data: Dict[str, Any], is_closed: bool) -> Tuple[Dict[str, Any], int]
    """🔥 НОВАЯ: Рассчитать все индикаторы в реальном времени (возвращает индикаторы + общее время)"""

async def _calculate_indicators(self, symbol: str, timeframe: str, candle_data: Dict[str, Any], is_closed: bool) -> Dict[str, Any]
    """Рассчитать все индикаторы для свечи"""

async def _calculate_volume_change(self, symbol: str, timeframe: str, candle_data: Dict[str, Any]) -> Optional[float]
    """Рассчитать изменение объема"""

async def _process_rsi_signals_real_time(self, session: AsyncSession, symbol: str, timeframe: str, rsi_value: float, price: float, processing_time_ms: int, volume_change_percent: Optional[float]) -> int
    """🔥 НОВАЯ: Обработать RSI сигналы в реальном времени"""

async def _process_rsi_signals(self, session: AsyncSession, symbol: str, timeframe: str, rsi_value: float, price: float, volume_change_percent: Optional[float]) -> int
    """Обработать RSI сигналы"""

async def _process_ema_signals_real_time(self, session: AsyncSession, symbol: str, timeframe: str, ema_values: Dict[int, float], price: float, processing_time_ms: int) -> int
    """🔥 НОВАЯ: Обработать EMA сигналы в реальном времени"""

async def _process_ema_signals(self, session: AsyncSession, symbol: str, timeframe: str, ema_values: Dict[int, float], price: float) -> int
    """Обработать EMA сигналы"""

def get_processing_stats(self) -> Dict[str, Any]
    """Получить статистику обработки"""

def get_real_time_performance_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику производительности реального времени"""

def reset_stats(self) -> None
    """Сбросить статистику"""

async def validate_processing_performance(self) -> Dict[str, bool]
    """🔥 НОВАЯ: Проверить соответствие целевым показателям производительности"""
```

**Глобальный экземпляр:** `signal_aggregator = SignalAggregator()`

### 📂 `src/services/notifications/`

#### 📄 `src/services/notifications/telegram_sender.py`
**Назначение:** Отправка уведомлений в Telegram

**Класс:**
```python
class TelegramSender:
    """🔥 ОБНОВЛЕН: Сервис отправки сообщений в Telegram с метриками реального времени"""
```

**Методы:**
```python
def __init__(self, bot: Bot)
    """Инициализация с экземпляром бота"""

async def send_signal_notification_real_time(self, user_id: int, signal_data: Dict[str, Any], processing_time_ms: int) -> Tuple[bool, int]
    """🔥 НОВАЯ: Отправить уведомление о сигнале реального времени (возвращает успех + время доставки)"""

async def send_signal_notification(self, user_id: int, signal_data: Dict[str, Any]) -> bool
    """Отправить уведомление о сигнале"""

async def send_message_to_user(self, user_id: int, text: str, reply_markup: Optional[InlineKeyboardMarkup] = None) -> bool
    """Отправить сообщение пользователю"""

async def send_message_with_retry(self, user_id: int, text: str, reply_markup: Optional[InlineKeyboardMarkup] = None, max_retries: int = 3) -> bool
    """Отправить сообщение с повторными попытками"""

async def handle_blocked_user(self, user_id: int) -> None
    """Обработать заблокированного пользователя"""

async def handle_user_deactivated(self, user_id: int) -> None
    """Обработать деактивированного пользователя"""

async def send_bulk_notifications(self, notifications: List[Tuple[int, str, Optional[InlineKeyboardMarkup]]]) -> Dict[str, int]
    """Отправить массовые уведомления"""

async def send_bulk_real_time_notifications(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]
    """🔥 НОВАЯ: Отправить массовые уведомления реального времени с метриками"""

def _create_signal_keyboard(self) -> InlineKeyboardMarkup
    """Создать клавиатуру для сигнала"""

async def _log_delivery_status(self, user_id: int, success: bool, error: Optional[str] = None) -> None
    """Логировать статус доставки"""

async def _log_real_time_delivery(self, user_id: int, success: bool, delivery_time_ms: int, processing_time_ms: int) -> None
    """🔥 НОВАЯ: Логировать доставку реального времени"""

def get_delivery_stats(self) -> Dict[str, int]
    """Получить статистику доставки"""

def get_real_time_delivery_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику доставки реального времени"""

def reset_stats(self) -> None
    """Сбросить статистику"""
```

📄 src/services/notifications/message_formatter.py
Назначение: Форматирование уведомлений и сообщений
Класс:
pythonclass MessageFormatter:
    """🔥 ОБНОВЛЕН: Сервис форматирования сообщений с поддержкой реального времени"""
Методы:
pythondef __init__(self)
    """Инициализация форматировщика"""

def format_signal_message(self, symbol: str, timeframe: str, price: float, price_change_percent: Optional[float] = None, rsi_value: Optional[float] = None, rsi_signal_type: Optional[str] = None, volume_change_percent: Optional[float] = None, ema_trend: Optional[str] = None, signal_type: str = "rsi_signal") -> str
    """Форматировать сообщение о сигнале"""

def format_real_time_signal_message(self, symbol: str, timeframe: str, price: float, signal_data: Dict[str, Any], processing_time_ms: int, total_time_ms: int) -> str
    """🔥 НОВАЯ: Форматировать сообщение сигнала реального времени с метриками времени"""

def format_rsi_signal(self, symbol: str, timeframe: str, rsi_value: float, signal_type: str, price: float, volume_change: Optional[float] = None) -> str
    """Форматировать RSI сигнал"""

def format_ema_signal(self, symbol: str, timeframe: str, ema_data: Dict[str, Any], price: float) -> str
    """Форматировать EMA сигнал"""

def format_price(self, price: float, precision: int = 8) -> str
    """Форматировать цену"""

def format_percentage(self, percentage: float, precision: int = 2) -> str
    """Форматировать процентное значение"""

def format_volume_change(self, volume_change: float) -> str
    """Форматировать изменение объема"""

def get_signal_emoji(self, signal_type: str) -> str
    """Получить эмодзи для типа сигнала"""

def get_trend_emoji(self, trend: str) -> str
    """Получить эмодзи для тренда"""

def get_timeframe_display(self, timeframe: str) -> str
    """Получить отображаемое название таймфрейма"""

def create_signal_header(self, signal_type: str, symbol: str, timeframe: str) -> str
    """Создать заголовок сигнала"""

def create_price_section(self, price: float, price_change: Optional[float] = None) -> str
    """Создать секцию с ценой"""

def create_indicator_section(self, rsi_value: Optional[float] = None, ema_data: Optional[Dict] = None) -> str
    """Создать секцию с индикаторами"""

def create_volume_section(self, volume_change: Optional[float] = None) -> str
    """Создать секцию с объемом"""

def create_footer_section(self) -> str
    """Создать подвал сообщения"""

def create_real_time_performance_section(self, processing_time_ms: int, total_time_ms: int) -> str
    """🔥 НОВАЯ: Создать секцию с производительностью реального времени"""

def format_timing_display(self, time_ms: int) -> str
    """🔥 НОВАЯ: Форматировать отображение времени"""
Глобальные функции:
pythondef format_signal_message(symbol: str, timeframe: str, signal_data: Dict[str, Any]) -> str
    """Глобальная функция форматирования сигнала"""

def format_real_time_signal_message(symbol: str, timeframe: str, signal_data: Dict[str, Any], timing_data: Dict[str, int]) -> str
    """🔥 НОВАЯ: Глобальная функция форматирования сигнала реального времени"""
📄 src/services/notifications/notification_queue.py
Назначение: Очередь уведомлений для асинхронной отправки
Класс:
pythonclass NotificationQueue:
    """🔥 ОБНОВЛЕНА: Очередь уведомлений с приоритетом для реального времени"""
Методы:
pythondef __init__(self)
    """Инициализация очереди"""

async def start_processing(self) -> None
    """Запустить обработку очереди"""

async def stop_processing(self) -> None
    """Остановить обработку очереди"""

async def add_notification(self, user_id: int, message: str, reply_markup: Optional[InlineKeyboardMarkup] = None, priority: int = 0) -> None
    """Добавить уведомление в очередь"""

async def add_real_time_notification(self, user_id: int, message: str, processing_time_ms: int, priority: int = 10, reply_markup: Optional[InlineKeyboardMarkup] = None) -> None
    """🔥 НОВАЯ: Добавить уведомление реального времени с высоким приоритетом"""

async def add_signal_notification(self, user_id: int, signal_data: Dict[str, Any]) -> None
    """Добавить уведомление о сигнале"""

async def process_notifications(self) -> None
    """🔥 ОБНОВЛЕНА: Обработать уведомления из очереди с приоритетом реального времени"""

async def _process_single_notification(self, notification: Dict[str, Any]) -> bool
    """Обработать одно уведомление"""

async def _process_real_time_notification(self, notification: Dict[str, Any]) -> Tuple[bool, int]
    """🔥 НОВАЯ: Обработать уведомление реального времени (возвращает успех + время доставки)"""

async def _handle_processing_error(self, notification: Dict[str, Any], error: Exception) -> None
    """Обработать ошибку при отправке"""

def get_queue_stats(self) -> Dict[str, Any]
    """🔥 ОБНОВЛЕНА: Получить статистику очереди + реальное время"""

def get_queue_size(self) -> int
    """Получить размер очереди"""

def get_real_time_queue_size(self) -> int
    """🔥 НОВАЯ: Получить размер очереди реального времени"""

def is_processing(self) -> bool
    """Проверить обрабатывается ли очередь"""

async def clear_queue(self) -> int
    """Очистить очередь"""

async def retry_failed_notifications(self) -> int
    """Повторить неудачные уведомления"""

def get_real_time_processing_stats(self) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить статистику обработки реального времени"""
Глобальный экземпляр: notification_queue = NotificationQueue()
📂 src/services/cache/
📄 src/services/cache/candle_cache.py
Назначение: Кеш для свечных данных в Redis
Класс:
pythonclass CandleCache:
    """🔥 ОБНОВЛЕН: Кеш свечных данных в Redis с оптимизацией для реального времени"""
Методы:
pythondef __init__(self)
    """Инициализация кеша свечей"""

async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]
    """Получить свечи из кеша"""

async def add_new_candle(self, symbol: str, timeframe: str, candle_data: Dict[str, Any]) -> bool
    """Добавить новую свечу в кеш"""

async def update_last_candle_real_time(self, symbol: str, timeframe: str, candle_data: Dict[str, Any]) -> bool
    """🔥 НОВАЯ: Обновить последнюю свечу в реальном времени (оптимизировано)"""

async def update_last_candle(self, symbol: str, timeframe: str, candle_data: Dict[str, Any]) -> bool
    """Обновить последнюю (текущую) свечу"""

async def cache_historical_data(self, symbol: str, timeframe: str, candles: List[Dict[str, Any]]) -> bool
    """Кешировать исторические данные"""

async def clear_cache(self, symbol: str, timeframe: Optional[str] = None) -> bool
    """Очистить кеш для символа"""

async def get_last_candle(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]
    """Получить последнюю свечу"""

async def get_last_price_real_time(self, symbol: str, timeframe: str) -> Optional[float]
    """🔥 НОВАЯ: Получить последнюю цену для расчетов реального времени"""

async def get_candles_count(self, symbol: str, timeframe: str) -> int
    """Получить количество свечей в кеше"""

async def get_recent_prices(self, symbol: str, timeframe: str, count: int = 14) -> List[float]
    """🔥 НОВАЯ: Получить последние цены для расчета индикаторов"""

def _get_cache_key(self, symbol: str, timeframe: str) -> str
    """Получить ключ кеша для свечей"""

def _get_real_time_key(self, symbol: str, timeframe: str) -> str
    """🔥 НОВАЯ: Получить ключ для данных реального времени"""

def _serialize_candle(self, candle_data: Dict[str, Any]) -> str
    """Сериализовать свечу для Redis"""

def _deserialize_candle(self, candle_str: str) -> Dict[str, Any]
    """Десериализовать свечу из Redis"""

async def _trim_cache(self, cache_key: str, max_size: int = 500) -> None
    """Обрезать кеш до максимального размера"""

async def get_cache_stats(self) -> Dict[str, Any]
    """Получить статистику кеша"""

async def warm_up_cache(self, symbols: List[str], timeframes: List[str]) -> Dict[str, bool]
    """Прогреть кеш для символов и таймфреймов"""

async def optimize_for_real_time(self) -> None
    """🔥 НОВАЯ: Оптимизировать кеш для работы реального времени"""
Глобальный экземпляр: candle_cache = CandleCache()
📄 src/services/cache/indicator_cache.py
Назначение: Кеш для значений индикаторов
Класс:
pythonclass IndicatorCache:
    """🔥 ОБНОВЛЕН: Кеш индикаторов в Redis с оптимизацией для реального времени"""
Методы:
pythondef __init__(self)
    """Инициализация кеша индикаторов"""

async def get_rsi(self, symbol: str, timeframe: str, period: int = 14) -> Optional[float]
    """Получить значение RSI из кеша"""

async def set_rsi_real_time(self, symbol: str, timeframe: str, period: int, value: float, ttl: int = 30) -> bool
    """🔥 НОВАЯ: Сохранить значение RSI в кеш с коротким TTL для реального времени"""

async def set_rsi(self, symbol: str, timeframe: str, period: int, value: float, ttl: int = 300) -> bool
    """Сохранить значение RSI в кеш"""

async def get_rsi_with_previous(self, symbol: str, timeframe: str, period: int = 14) -> Tuple[Optional[float], Optional[float]]
    """🔥 НОВАЯ: Получить текущее и предыдущее значение RSI"""

async def get_ema(self, symbol: str, timeframe: str, period: int) -> Optional[float]
    """Получить значение EMA из кеша"""

async def set_ema_real_time(self, symbol: str, timeframe: str, period: int, value: float, ttl: int = 30) -> bool
    """🔥 НОВАЯ: Сохранить значение EMA в кеш с коротким TTL для реального времени"""

async def set_ema(self, symbol: str, timeframe: str, period: int, value: float, ttl: int = 300) -> bool
    """Сохранить значение EMA в кеш"""

async def get_multiple_ema_real_time(self, symbol: str, timeframe: str, periods: List[int]) -> Dict[int, Optional[float]]
    """🔥 НОВАЯ: Получить несколько значений EMA одновременно"""

async def set_multiple_ema_real_time(self, symbol: str, timeframe: str, ema_values: Dict[int, float], ttl: int = 30) -> bool
    """🔥 НОВАЯ: Сохранить несколько значений EMA одновременно"""

async def get_volume_change(self, symbol: str, timeframe: str) -> Optional[float]
    """Получить изменение объема из кеша"""

async def set_volume_change(self, symbol: str, timeframe: str, value: float, ttl: int = 120) -> bool
    """Сохранить изменение объема в кеш"""

async def get_all_indicators(self, symbol: str, timeframe: str) -> Dict[str, Any]
    """Получить все индикаторы для символа и таймфрейма"""

async def get_all_indicators_real_time(self, symbol: str, timeframe: str) -> Dict[str, Any]
    """🔥 НОВАЯ: Получить все индикаторы для реального времени с временными метками"""

async def invalidate_indicators(self, symbol: str, timeframe: Optional[str] = None) -> bool
    """Инвалидировать кеш индикаторов"""

async def save_indicator_state(self, symbol: str, timeframe: str, indicator_type: str, state: Dict[str, Any]) -> bool
    """🔥 НОВАЯ: Сохранить состояние индикатора для инкрементальных обновлений"""

async def get_indicator_state(self, symbol: str, timeframe: str, indicator_type: str) -> Optional[Dict[str, Any]]
    """🔥 НОВАЯ: Получить состояние индикатора"""

def _get_rsi_key(self, symbol: str, timeframe: str, period: int) -> str
    """Получить ключ для RSI"""

def _get_ema_key(self, symbol: str, timeframe: str, period: int) -> str
    """Получить ключ для EMA"""

def _get_volume_key(self, symbol: str, timeframe: str) -> str
    """Получить ключ для изменения объема"""

def _get_state_key(self, symbol: str, timeframe: str, indicator_type: str) -> str
    """🔥 НОВАЯ: Получить ключ для состояния индикатора"""

def _get_real_time_key(self, base_key: str) -> str
    """🔥 НОВАЯ: Получить ключ для данных реального времени"""

async def get_cache_stats(self) -> Dict[str, Any]
    """Получить статистику кеша индикаторов"""

async def cleanup_expired_indicators(self) -> int
    """Очистить просроченные индикаторы"""

async def optimize_for_real_time(self) -> None
    """🔥 НОВАЯ: Оптимизировать кеш для работы реального времени"""
Глобальный экземпляр: indicator_cache = IndicatorCache()
📄 src/services/cache/real_time_cache.py 🔥 НОВЫЙ ФАЙЛ
Назначение: Специализированный кеш для данных реального времени
Класс:
pythonclass RealTimeCache:
    """Специализированный кеш для данных реального времени"""
Методы:
pythondef __init__(self)
    """Инициализация кеша реального времени"""

async def set_current_price(self, symbol: str, timeframe: str, price: float) -> bool
    """Сохранить текущую цену с минимальным TTL"""

async def get_current_price(self, symbol: str, timeframe: str) -> Optional[float]
    """Получить текущую цену"""

async def set_processing_metrics(self, operation_id: str, metrics: Dict[str, Any]) -> bool
    """Сохранить метрики обработки"""

async def get_processing_metrics(self, operation_id: str) -> Optional[Dict[str, Any]]
    """Получить метрики обработки"""

async def increment_processing_counter(self, counter_name: str) -> int
    """Увеличить счетчик обработки"""

async def get_processing_counters(self) -> Dict[str, int]
    """Получить все счетчики обработки"""

async def set_performance_alert(self, alert_type: str, data: Dict[str, Any], ttl: int = 300) -> bool
    """Установить предупреждение о производительности"""

async def get_performance_alerts(self) -> List[Dict[str, Any]]
    """Получить активные предупреждения о производительности"""

async def cleanup_old_metrics(self) -> int
    """Очистить старые метрики"""

def get_cache_performance_stats(self) -> Dict[str, Any]
    """Получить статистику производительности кеша"""
Глобальный экземпляр: real_time_cache = RealTimeCache()

🛠️ UTILS LAYER - УТИЛИТЫ
📄 src/utils/constants.py
Назначение: Все константы приложения
Основные константы:
python# Информация о приложении
APP_NAME: str = "CryptoBot"
APP_VERSION: str = "3.0.0"  # 🔥 ОБНОВЛЕНА версия

# Binance константы
BINANCE_TIMEFRAMES: List[str] = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
TIMEFRAME_TO_MS: Dict[str, int] = {...}  # Конвертация в миллисекунды
TIMEFRAME_NAMES: Dict[str, str] = {...}  # Человекочитаемые названия

# Индикаторы
RSI_PERIODS: List[int] = [14, 21, 30]
EMA_PERIODS: List[int] = [20, 50, 100, 200]

# 🔥 НОВЫЕ: Константы реального времени
REAL_TIME_PROCESSING_TARGETS: Dict[str, int] = {
    "websocket_processing": 10,    # < 10ms
    "rsi_calculation": 100,        # < 100ms
    "ema_calculation": 50,         # < 50ms
    "signal_generation": 200,      # < 200ms
    "notification_delivery": 500,  # < 500ms
    "total_processing": 1000       # < 1000ms
}

REAL_TIME_CACHE_TTL: Dict[str, int] = {
    "indicators": 30,              # 30 секунд
    "prices": 10,                  # 10 секунд
    "states": 300,                 # 5 минут
    "metrics": 60                  # 1 минута
}

# Эмодзи
EMOJI: Dict[str, str] = {...}
SIGNAL_EMOJIS: Dict[str, str] = {...}
TREND_EMOJIS: Dict[str, str] = {...}
PERFORMANCE_EMOJIS: Dict[str, str] = {  # 🔥 НОВЫЕ
    "fast": "⚡",
    "normal": "✅", 
    "slow": "⚠️",
    "critical": "🚨"
}

# Валюты
CURRENCY_SYMBOLS: Dict[str, str] = {...}
QUOTE_ASSETS: List[str] = ["USDT", "BUSD", "BTC", "ETH", "BNB"]

# Интервалы повтора сигналов
SIGNAL_REPEAT_INTERVALS: Dict[str, int] = {...}

# 🔥 НОВЫЕ: Интервалы реального времени
REAL_TIME_INTERVALS: Dict[str, int] = {
    "rsi_signal_repeat": 60,       # 1 минута
    "ema_signal_repeat": 120,      # 2 минуты  
    "performance_check": 30,       # 30 секунд
    "cache_cleanup": 300           # 5 минут
}

# Регулярные выражения
REGEX_PATTERNS: Dict[str, str] = {...}

# Лимиты
MIN_SYMBOL_LENGTH: int = 3
MAX_SYMBOL_LENGTH: int = 20
MAX_PAIRS_PER_USER: int = 50
MAX_REAL_TIME_PAIRS: int = 20      # 🔥 НОВАЯ: Лимит пар реального времени
Функции:
pythondef get_timeframe_ms(timeframe: str) -> int
    """Получить количество миллисекунд для таймфрейма"""

def get_signal_emoji(signal_type: str) -> str
    """Получить эмодзи для типа сигнала"""

def get_currency_symbol(currency: str) -> str
    """Получить символ валюты"""

def is_valid_timeframe(timeframe: str) -> bool
    """Проверить валидность таймфрейма"""

def get_repeat_interval(signal_type: str) -> int
    """Получить интервал повторения для типа сигнала"""

def get_real_time_target(operation: str) -> int
    """🔥 НОВАЯ: Получить целевое время для операции реального времени"""

def get_performance_emoji(time_ms: int, target_ms: int) -> str
    """🔥 НОВАЯ: Получить эмодзи производительности"""

def is_real_time_performance_good(time_ms: int, operation: str) -> bool
    """🔥 НОВАЯ: Проверить хорошая ли производительность"""
📄 src/utils/exceptions.py
Назначение: Кастомные исключения
Базовое исключение:
pythonclass CryptoBotError(Exception):
    """Базовое исключение для крипто-бота"""
🔥 НОВЫЕ: Исключения реального времени:
pythonclass RealTimeError(CryptoBotError):
    """Ошибки системы реального времени"""

class PerformanceError(RealTimeError):
    """Ошибка производительности реального времени"""

class IndicatorCalculationTimeoutError(RealTimeError):
    """Превышено время расчета индикатора"""

class RealTimeProcessingError(RealTimeError):
    """Ошибка обработки реального времени"""
Остальные исключения:
pythonclass ConfigurationError(CryptoBotError):
    """Ошибки конфигурации"""

class DatabaseError(CryptoBotError):
    """Ошибки базы данных"""

class RedisError(CryptoBotError):
    """Ошибки Redis"""

class WebSocketConnectionError(CryptoBotError):
    """Ошибка WebSocket подключения"""

class BinanceAPIError(CryptoBotError):
    """Ошибки Binance API"""

class SignalError(CryptoBotError):
    """Ошибки генерации сигналов"""
📄 src/utils/validators.py
Назначение: Валидаторы входных данных
Функции валидации символов:
pythondef validate_trading_pair_symbol(symbol: str) -> tuple[bool, Optional[str]]
    """Валидировать символ торговой пары"""

def extract_base_quote_assets(symbol: str) -> Optional[Tuple[str, str]]
    """Извлечь базовую и котируемую валюты из символа"""

def normalize_trading_symbol(symbol: str) -> str
    """Нормализовать символ торговой пары"""
🔥 НОВЫЕ: Функции валидации реального времени:
pythondef validate_processing_time(time_ms: int, operation: str) -> tuple[bool, Optional[str]]
    """Валидировать время обработки реального времени"""

def validate_real_time_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]
    """Валидировать конфигурацию реального времени"""

def validate_performance_metrics(metrics: Dict[str, Any]) -> tuple[bool, Optional[str]]
    """Валидировать метрики производительности"""
Остальные функции валидации:
pythondef validate_timeframe(timeframe: str) -> tuple[bool, Optional[str]]
def validate_price(price: Union[str, float, Decimal]) -> tuple[bool, Optional[str]]
def validate_rsi_value(rsi: Union[str, float]) -> tuple[bool, Optional[str]]
def validate_binance_kline_data_detailed(kline_data: Dict[str, Any]) -> tuple[bool, str]
📄 src/utils/time_helpers.py
Назначение: Функции для работы со временем
Функции временных меток:
pythondef get_current_timestamp() -> int
    """Получить текущую временную метку в миллисекундах"""

def get_high_precision_timestamp() -> int
    """🔥 НОВАЯ: Получить временную метку с высокой точностью для реального времени"""

def timestamp_to_datetime(timestamp: int, in_milliseconds: bool = True) -> datetime
    """Преобразовать Unix timestamp в datetime объект"""

def datetime_to_timestamp(dt: datetime, in_milliseconds: bool = True) -> int
    """Преобразовать datetime в Unix timestamp"""
🔥 НОВЫЕ: Функции реального времени:
pythondef measure_execution_time(func):
    """Декоратор для измерения времени выполнения функции"""

def get_time_since_ms(start_time: int) -> int
    """Получить прошедшее время в миллисекундах"""

def is_within_time_target(elapsed_ms: int, target_ms: int) -> bool
    """Проверить укладывается ли время в целевые показатели"""

def format_execution_time(time_ms: int) -> str
    """Форматировать время выполнения для отображения"""
Функции таймфреймов:
pythondef timeframe_to_milliseconds(timeframe: str) -> Optional[int]
def get_timeframe_display_name(timeframe: str) -> str
def align_timestamp_to_timeframe(timestamp: int, timeframe: str) -> int
def calculate_time_until_next_candle(timeframe: str, current_time: Optional[int] = None) -> int
📄 src/utils/math_helpers.py
Назначение: Математические функции для расчетов
Базовые математические функции:
pythondef safe_divide(dividend: Union[float, Decimal], divisor: Union[float, Decimal]) -> float
def calculate_percentage_change(old_value: float, new_value: float) -> float
def round_to_precision(value: Union[float, Decimal], precision: int) -> float
def clamp_value(value: float, min_value: float, max_value: float) -> float
Функции скользящих средних:
pythondef calculate_simple_moving_average(values: List[float], period: int) -> Optional[float]
def calculate_exponential_moving_average(values: List[float], period: int, previous_ema: Optional[float] = None) -> Optional[float]
def calculate_ema_incremental(current_price: float, previous_ema: float, period: int) -> float
    """🔥 НОВАЯ: Инкрементальный расчет EMA для реального времени"""
Функции для индикаторов:
pythondef calculate_rsi_basic(prices: List[float], period: int = 14) -> Optional[float]
def calculate_rsi_incremental(current_price: float, previous_price: float, avg_gain: float, avg_loss: float, period: int = 14) -> Tuple[float, float, float]
    """🔥 НОВАЯ: Инкрементальный расчет RSI (возвращает RSI, новый avg_gain, новый avg_loss)"""
🔥 НОВЫЕ: Функции оптимизации производительности:
pythondef calculate_performance_score(actual_time_ms: int, target_time_ms: int) -> float
    """Рассчитать оценку производительности (0-1)"""

def detect_performance_degradation(recent_times: List[int], target_time: int, threshold: float = 0.2) -> bool
    """Определить деградацию производительности"""

def calculate_moving_average_performance(times: List[int], window: int = 10) -> float
    """Рассчитать скользящее среднее производительности"""
📄 src/utils/logger.py
Назначение: Система логирования
Функции настройки:
pythondef setup_logging(log_level: Optional[str] = None, json_logs: bool = False, log_file: Optional[str] = None) -> None
def get_logger(name: str) -> Any
def configure_structlog() -> None
def setup_real_time_logging() -> None
    """🔥 НОВАЯ: Настроить логирование для реального времени"""
Функции логирования событий:
pythondef log_user_action(action: str, user_id: int, **kwargs) -> None
def log_websocket_event(event: str, **kwargs) -> None
def log_signal_generated(signal_type: str, symbol: str, timeframe: str, **kwargs) -> None

def log_real_time_processing(operation: str, symbol: str, timeframe: str, processing_time_ms: int, **kwargs) -> None
    """🔥 НОВАЯ: Логировать обработку реального времени"""

def log_performance_alert(alert_type: str, details: Dict[str, Any]) -> None
    """🔥 НОВАЯ: Логировать предупреждение о производительности"""

def log_indicator_calculation(indicator_type: str, symbol: str, timeframe: str, calculation_time_ms: int, **kwargs) -> None
    """🔥 НОВАЯ: Логировать расчет индикатора"""
Классы:
pythonclass LoggerMixin:
    """Миксин для добавления логирования в классы"""
    
    def log_real_time_event(self, event: str, processing_time_ms: int, **kwargs) -> None
        """🔥 НОВАЯ: Логировать событие реального времени"""
    
    def log_performance_metric(self, metric_name: str, value: float, **kwargs) -> None
        """🔥 НОВАЯ: Логировать метрику производительности"""
🔥 НОВЫЙ КЛАСС: Логгер производительности:
pythonclass PerformanceLogger(LoggerMixin):
    """Специализированный логгер для метрик производительности"""
    
    def start_operation(self, operation_id: str, operation_type: str, **kwargs) -> str
    def end_operation(self, timing_id: str, success: bool = True, **kwargs) -> int
    def log_slow_operation(self, operation_type: str, actual_time_ms: int, target_time_ms: int, **kwargs) -> None
    def generate_performance_report(self) -> Dict[str, Any]
📄 src/utils/performance_utils.py 🔥 НОВЫЙ ФАЙЛ
Назначение: Утилиты для мониторинга производительности
Декораторы:
pythondef measure_time(target_ms: Optional[int] = None):
    """Декоратор для измерения времени выполнения функции"""

def log_slow_operations(target_ms: int):
    """Декоратор для логирования медленных операций"""

def monitor_real_time_performance(operation_type: str):
    """Декоратор для мониторинга производительности реального времени"""
Классы мониторинга:
pythonclass TimingContext:
    """Контекстный менеджер для измерения времени"""
    
    def __init__(self, operation_name: str, target_ms: Optional[int] = None)
    def __enter__(self) -> "TimingContext"
    def __exit__(self, exc_type, exc_val, exc_tb) -> None
    
    @property
    def elapsed_ms(self) -> int
    
    @property
    def is_within_target(self) -> bool
Функции мониторинга:
pythondef create_performance_alert(operation: str, actual_time_ms: int, target_time_ms: int) -> Dict[str, Any]
def calculate_performance_percentile(times: List[int], percentile: float = 95.0) -> float
def detect_performance_regression(current_times: List[int], baseline_times: List[int]) -> bool
def generate_performance_summary(metrics: Dict[str, List[int]]) -> Dict[str, Any]

⚙️ CONFIG LAYER - КОНФИГУРАЦИЯ
📄 src/config/bot_config.py
Назначение: Конфигурация Telegram бота
Класс конфигурации:
pythonclass BotConfig(BaseSettings):
    """🔥 ОБНОВЛЕНА: Конфигурация Telegram бота с настройками реального времени"""
    
    # Основные настройки
    bot_token: str
    debug: bool
    log_level: str
    max_connections: int
    request_timeout: int
    
    # 🔥 НОВЫЕ: Настройки реального времени
    real_time_enabled: bool
    real_time_processing_timeout: int
    real_time_performance_monitoring: bool
    real_time_alerts_enabled: bool
    
    # Целевые показатели производительности
    target_websocket_processing_ms: int = 10
    target_rsi_calculation_ms: int = 100
    target_ema_calculation_ms: int = 50
    target_signal_generation_ms: int = 200
    target_notification_delivery_ms: int = 500
    target_total_processing_ms: int = 1000
    
    # Настройки уведомлений
    notification_rate_limit: int
    signal_check_interval: int
    real_time_signal_repeat_interval: int  # 🔥 НОВОЕ
    
    # Дефолтные настройки
    default_timeframes: List[str]
    default_pair: str
    rsi_period: int
    ema_periods: List[int]
    
    # Зоны RSI
    rsi_oversold_strong: float
    rsi_oversold_medium: float
    rsi_oversold_normal: float
    rsi_overbought_normal: float
    rsi_overbought_medium: float
    rsi_overbought_strong: float
    
    # Интервалы повтора сигналов
    signal_repeat_interval: int
Функции:
pythondef get_bot_config() -> BotConfig
def is_debug_mode() -> bool
def get_rsi_zones() -> Dict[str, float]
def validate_config() -> None
def get_default_timeframes() -> List[str]
def get_notification_settings() -> Dict[str, Any]

def is_real_time_enabled() -> bool
    """🔥 НОВАЯ: Проверить включено ли реальное время"""

def get_performance_targets() -> Dict[str, int]
    """🔥 НОВАЯ: Получить целевые показатели производительности"""

def get_real_time_settings() -> Dict[str, Any]
    """🔥 НОВАЯ: Получить настройки реального времени"""
📄 src/config/real_time_config.py 🔥 НОВЫЙ ФАЙЛ
Назначение: Специализированная конфигурация для реального времени
Класс конфигурации:
pythonclass RealTimeConfig(BaseSettings):
    """Конфигурация системы реального времени"""
    
    # Основные настройки
    enabled: bool = True
    max_concurrent_processing: int = 100
    processing_queue_size: int = 1000
    
    # Целевые показатели производительности (в миллисекундах)
    target_websocket_processing: int = 10
    target_rsi_calculation: int = 100
    target_ema_calculation: int = 50
    target_signal_generation: int = 200
    target_notification_delivery: int = 500
    target_total_processing: int = 1000
    
    # Пороги предупреждений
    warning_threshold_multiplier: float = 1.5
    critical_threshold_multiplier: float = 2.0
    
    # Настройки мониторинга
    performance_monitoring_enabled: bool = True
    performance_logging_enabled: bool = True
    alert_on_performance_degradation: bool = True
    
    # Настройки кеширования
    indicator_cache_ttl: int = 30
    price_cache_ttl: int = 10
    state_cache_ttl: int = 300
    metrics_cache_ttl: int = 60
    
    # Настройки очистки
    cleanup_interval: int = 300
    max_metrics_age: int = 3600
    max_old_indicators_age: int = 86400
    
    # Настройки отчетности
    generate_performance_reports: bool = True
    report_generation_interval: int = 3600
    detailed_performance_logging: bool = True
Функции:
pythondef get_real_time_config() -> RealTimeConfig
def is_real_time_enabled() -> bool
def get_performance_targets() -> Dict[str, int]
def get_performance_thresholds() -> Dict[str, Dict[str, int]]
def get_cache_settings() -> Dict[str, int]
def validate_real_time_config() -> None
def get_monitoring_settings() -> Dict[str, bool]
def should_alert_on_performance(operation: str, time_ms: int) -> Tuple[bool, str]
📄 Остальные конфигурации
Обновлены с настройками реального времени:

database_config.py - добавлены настройки пула для реального времени
redis_config.py - добавлены настройки кеширования реального времени
binance_config.py - добавлены настройки WebSocket для реального времени
logging_config.py - добавлены настройки логирования производительности


🔍 БЫСТРЫЙ ПОИСК ПО ФУНКЦИЯМ
🚀 Реальное время - ключевые функции:

Главный процессор: src/services/real_time/real_time_processor.py → process_websocket_data()
RSI реального времени: src/services/indicators/rsi_calculator.py → calculate_real_time_rsi()
EMA реального времени: src/services/indicators/ema_calculator.py → calculate_real_time_ema()
Мониторинг производительности: src/services/real_time/performance_monitor.py → check_performance_targets()
Кеш реального времени: src/services/cache/real_time_cache.py → set_current_price()

⚡ Оптимизация производительности:

Инкрементальный RSI: src/services/indicators/rsi_calculator.py → update_rsi_incremental()
Инкрементальный EMA: src/services/indicators/ema_calculator.py → update_ema_incremental()
Измерение времени: src/utils/performance_utils.py → TimingContext
Алерты производительности: src/services/real_time/performance_monitor.py → alert_on_performance_degradation()

🎯 Целевые показатели:
WebSocket → Обработка:     < 10ms   ⚡
RSI расчет:               < 100ms   📊
EMA расчет:               < 50ms    📈
Генерация сигналов:       < 200ms   🚨
Отправка уведомлений:     < 500ms   📱
🎯 ОБЩЕЕ ВРЕМЯ:           < 1000ms

📈 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ РЕАЛЬНОГО ВРЕМЕНИ
📊 Мониторинг и алерты:

Предупреждение: 150% от целевого времени ⚠️
Критично: 200% от целевого времени 🚨
Автоматические отчеты: каждый час 📋
Очистка метрик: каждые 5 минут 🧹


📝 ЗАКЛЮЧЕНИЕ
Эта полная версия 3.0 документации содержит ДЕТАЛЬНУЮ ИНТЕГРАЦИЮ ТРЕБОВАНИЙ РЕАЛЬНОГО ВРЕМЕНИ с исходной архитектурой проекта.
🔥 КЛЮЧЕВЫЕ ДОБАВЛЕНИЯ:
⚡ Система реального времени:

Новый модуль: src/services/real_time/ с процессором и монитором производительности
Инкрементальные алгоритмы: RSI и EMA без полного пересчета
Специализированный кеш: для данных реального времени с коротким TTL
Мониторинг производительности: с автоматическими алертами

📊 Оптимизированные индикаторы:

RSI: calculate_real_time_rsi() с возвратом времени обработки
EMA: calculate_real_time_ema() с инкрементальным алгоритмом
Кеширование состояний: для быстрых обновлений
Метрики времени: для каждого расчета

🚨 Улучшенные сигналы:

Контекст тренда: учет предыдущих значений RSI
Метрики производительности: время обработки в каждом сигнале
Приоритетная очередь: для уведомлений реального времени
Детальное логирование: всех этапов обработки

Этот AGENTS.MD готов для разработки высокопроизводительного крипто-бота с полной поддержкой реального времени!