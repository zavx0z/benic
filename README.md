## Docker

stop and rm data

```shell
docker stop db && sudo rm -rf ../store/data/
```

Postgresql база данных запуск

```shell
sh ./scripts/startDB.sh
```

## Alembic

```shell
alembic init -t async migrations
```

```shell
alembic revision --autogenerate -m 'User'
```

```shell
alembic upgrade head
```

-----------------------------------------------------------------------------------

## .env

```shell
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
```

------------------------------------------------------------------------------------
