#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_DB $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

flask db upgrade
celery -A flask_app.celery worker --loglevel=info
gunicorn --worker-class eventlet -w 1 flask_app:app
exec "$@"
