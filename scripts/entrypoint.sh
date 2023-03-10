#!/bin/bash
set -e
# Ожидаем соединение с базой данных
/scripts/wait-for-postgres.sh
# Запускаем миграции базы данных приложения
alembic upgrade head
# Запускаем приложение
exec uvicorn app:app --host 0.0.0.0 --port 8000
