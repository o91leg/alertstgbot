#!/bin/bash
echo "🔍 Health check for CryptoBot..."

# Проверка процессов
if pgrep -f "python.*src.main" > /dev/null; then
    echo "✅ Bot process is running"
else
    echo "❌ Bot process is not running"
    exit 1
fi

echo "✅ Health check completed"
