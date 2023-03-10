from sqlalchemy import select

from auth.models import User
from shared.db import  async_session


async def get_user(pk):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == pk))
        user = result.scalars().first()
        if not user:
            return None
        return user
