from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User


async def create_user(engine, user_data):
    async with engine.begin() as conn:
        session = AsyncSession(bind=conn)
        user = User(username=user_data["username"], email=user_data["email"], hashed_password=user_data["password"])
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user(engine, user_id):
    async with engine.begin() as conn:
        session = AsyncSession(bind=conn, selectinload(User.dialogs))
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
    return user


async def update_user(engine, user_id, user_data):
    async with engine.begin() as conn:
        session = AsyncSession(bind=conn)
        user = await session.get(User, user_id)
        if user is not None:
            for key, value in user_data.items():
                setattr(user, key, value)
            await session.commit()
    return user


async def delete_user(engine, user_id):
    async with engine.begin() as conn:
        session = AsyncSession(bind=conn)
        user = await session.get(User, user_id)
        if user is not None:
            session.delete(user)
            await session.commit()


async def main():
    engine = None
    # Создание пользователя
    user_data = {"username": "john_doe", "email": "johndoe@example.com", "password": "securepassword"}
    created_user = await create_user(engine, user_data)
    print(created_user)
    # Получение пользователя
    retrieved_user = await get_user(engine, created_user.id)
    print(retrieved_user)
    # Обновление пользователя
    updated_user_data = {"email": "newemail@example.com"}
    updated_user = await update_user(engine, created_user.id, updated_user_data)
    print(updated_user)
    # Удаление пользователя
    await delete_user(engine, created_user.id)


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
