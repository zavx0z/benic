## APP

killport

```shell
sudo lsof -t -i tcp:8000 | xargs kill -9
```

Сборка образа

```shell
docker build -t zavx0z:benic .
```

Запуск контейнера

```shell
docker run -d --rm \
  --name app \
  -e POSTGRES_USER=username \
  -e POSTGRES_PASSWORD=pswd \
  -e POSTGRES_DB=dbname \
  -e JWT_SECRET_KEY=jwtkey \
  -p 8080:8000 \
  zavx0z:benic
```

---

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
alembic revision --autogenerate -m 'init'
```

```shell
alembic upgrade head
```

---

## .env

```shell
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
```

---

## Dramatiq

```shell
dramatiq worker
```

#### Убить процессы

```shell
ps aux | grep dramatiq
kill 7382
```

# Windows

Использование команды «Создать среду»
Чтобы создать локальные среды в VS Code с использованием виртуальных сред или Anaconda, вы можете выполнить следующие действия: откройте палитру команд ( Ctrl+Shift+P ), найдите команду `Python: Create Environment` и выберите ее.
` Python: Select Interpreter`

[vsCode debug](https://fastapi.tiangolo.com/tutorial/debugging/)

`alembic upgrade head`

[firebase FCM serviceAccountKey.json](https://console.firebase.google.com/project/bots-work/settings/serviceaccounts/adminsdk)
