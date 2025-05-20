#!/bin/bash

echo "🚀 Запуск ProSkills backend..."

# 1. Перевірка наявності .env
if [ ! -f ".env" ]; then
  echo "❌ .env файл не знайдено. Створи його перед запуском."
  exit 1
fi

# 2. Активація poetry-оточення
echo "📦 Активація poetry-середовища..."
poetry install

# 3. Запуск FastAPI
echo "🧠 Запуск FastAPI (uvicorn)..."
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 5001

# 4. Після завершення
echo "✅ Сервер зупинено або завершився."

