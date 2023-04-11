from sqlalchemy import select

from messages.models.message import Message
from shared.db import async_session


async def create_message(text: str, sender_id: int, dialog_id: int):
    """Создание сообщения"""
    async with async_session() as session:
        message = Message(text=text, sender_id=sender_id, dialog_id=dialog_id)
        session.add(message)
        await session.commit()
        await session.refresh(message)
    return message


async def get_message_from_id(pk: int):
    """Получение сообщения"""
    async with async_session() as session:
        message = await session.execute(select(Message).where(Message.id == pk)).scalar()
    return message
