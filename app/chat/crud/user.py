from sqlalchemy.orm import selectinload
from sqlalchemy import select
from auth.models import User
from chat.models import Message
from shared.db import async_session


async def get_users_with_messages_by_owner_dialogs():
    async with async_session() as session:
        stmt = (
            select(User)
            .join(Message)
            .filter(User.is_superuser == False)
            .filter(Message.sender_id == User.id)
            .distinct()
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users
