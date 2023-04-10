import argparse
import asyncio
import sys

from sso.models import Role
from sso.routes.join import create_user
from shared.db import async_session


async def create_superuser_command(username: str, password: str):
    # Получаем подключение к базе данных
    async with async_session() as session:
        superuser = await create_user(session, username, password, Role.superuser)
        print(f"Superuser created with username: {username} and id: {superuser.id}")


parser = argparse.ArgumentParser()
parser.add_argument("username", help="Имя пользователя")
parser.add_argument("password", help="Пароль пользователя")
args = parser.parse_args()

try:
    asyncio.run(create_superuser_command(args.username, args.password))
    print(f"Пользователь {args.username} создан успешно")
    sys.exit(0)
except Exception as e:
    print(f"Ошибка при создании пользователя: {e}")
    sys.exit(1)
