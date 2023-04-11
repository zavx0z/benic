from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sso.models.user import User
from shared.db import async_session


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


async def get_user(pk):
    async with async_session() as session:
        # result = await session.execute(select(User).options(joinedload(User.dialogs)).where(User.id == pk))
        result = await session.execute(select(User).where(User.id == pk))
        user = result.scalars().first()
        if not user:
            return None
        else:
            await session.refresh(user)
            return user
