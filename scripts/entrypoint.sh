#!/bin/bash
set -e
# Устанавливаем переменную DRAMATIQ_LOGS
export DRAMATIQ_LOGS=/store/dramatiq

# Ожидаем соединение с базой данных
/scripts/wait-for-postgres.sh
# Запускаем миграции базы данных приложения
alembic upgrade head
# Запускаем приложение
exec uvicorn main:app --host 0.0.0.0 --port 8000 &
# Запускаем Dramatiq worker
exec python -m dramatiq worker --watch /app --processes 2 --threads 2 --log-file $DRAMATIQ_LOGS/dramatiq.log

#Здесь мы используем оператор & для запуска приложения в фоновом режиме,
# чтобы мы могли запустить Dramatiq worker в том же контейнере.
# Затем мы используем команду exec для запуска команды python -m dramatiq tasks в той же оболочке, что и ваше приложение.
# --watch /app указывает, что Dramatiq должен отслеживать задачи в каталоге /app,
# --processes 2 устанавливает количество процессов, которые будут обрабатывать задачи, а
# --threads 2 устанавливает количество потоков в каждом процессе. Эти значения можно настроить в соответствии с вашими потребностями.
# --logfile путь к файлу логов Dramatiq

