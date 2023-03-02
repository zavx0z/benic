# Наследуемся от образа Python версии 3.10
FROM python:3.10-slim-buster
# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Устанавливаем зависимости для PostgreSQL и Nginx
RUN apt-get update && apt-get install -y \
    libpq-dev \
    nginx \
 && rm -rf /var/lib/apt/lists/*
# Копируем конфигурационный файл Nginx
COPY tmp/nginx.conf /etc/nginx/nginx.conf
# Создаем директорию приложения внутри контейнера
RUN mkdir /app
# Копируем файлы зависимостей
COPY app/requirements.txt /app/
# Устанавливаем зависимости приложения
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
# Копируем файлы приложения внутрь контейнера
COPY . /app
# Указываем рабочую директорию
WORKDIR /app
# Копируем скрипт запуска миграций
COPY app/alembic.ini /app/alembic.ini
COPY alembic /app/alembic
# Создаем точку входа для запуска миграций и приложения
COPY tmp/start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT ["/start.sh"]
