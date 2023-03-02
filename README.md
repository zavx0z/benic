## APP

Сборка образа

```shell
docker build -t zavx0z:benic .
```

Запуск контейнера

```shell
docker run -d --rm \
  --name app \
  -e POSTGRES_USER=zavx0zBenif \
  -e POSTGRES_PASSWORD=12112022 \
  -e POSTGRES_DB=benif \
  -e JWT_SECRET_KEY='adkngdfFDGSDFqhnlakjflorqirefOJ;SJDG' \
  -p 8080:8000 \
  zavx0z:benic
```

----------------------------------------------------------------

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
