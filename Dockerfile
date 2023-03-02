# Используем базовый образ Python 3.9
FROM python:3.9
# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Устанавливаем зависимости для работы с PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client
# Устанавливаем рабочую директорию в контейнере
WORKDIR /app
# Копируем все файлы приложения в контейнер
COPY ./app /app
# устанавливаем зависимости
RUN pip install -r requirements.txt
# Копируем скрипты
COPY scripts /scripts
# Устанавливаем права на выполнение для скриптов
RUN chmod -R +x /scripts
# Запускаем entrypoint скрипт
ENTRYPOINT ["/scripts/entrypoint.sh"]