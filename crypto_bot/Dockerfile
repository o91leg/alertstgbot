FROM python:3.11-slim

# Установка системных зависимостей для производительности
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY .env.example .env
COPY scripts/ ./scripts/

# Создание директорий для логов и данных
RUN mkdir -p logs data

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app && \
    chmod +x scripts/*.sh

USER botuser

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV REAL_TIME_ENABLED=true

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; print('OK')" || exit 1

# Команда запуска
CMD ["python", "-m", "src.main"]
