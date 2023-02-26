## Docker

[install](https://wiki.crowncloud.net/?How_to_Install_Docker_On_Ubuntu_22_10)

```shell
docker run -d \
  --name db \
  -p 5432:5432 \
  -v $(pwd)/data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=12112022 \
  -e POSTGRES_USER=user \
  -e POSTGRES_DB=benic \
  -e POSTGRES_PORT=5432 \
  postgres:alpine

```

.env

```dotenv
SQLALCHEMY_DATABASE_URI=postgresql://user:12112022@localhost:5432/benic
```

migrations

```shell
flask db init
flask db migrate -m "message"
```

------------------------------
> ```shell
>flask db upgrade
>flask db downgrade
>```