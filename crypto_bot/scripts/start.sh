#!/bin/bash
echo "🚀 Starting CryptoBot v3.0..."
export PYTHONPATH=/app
export REAL_TIME_ENABLED=true
cd /app
python -m src.main
