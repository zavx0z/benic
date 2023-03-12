from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from chat.models import Message, Dialog, DialogParticipant
from shared.db import async_session


async def create_message(text: str, sender_id: int, dialog_id: int):
    """Создание сообщения"""
    async with async_session() as session:
        message = Message(text=text, sender_id=sender_id, dialog_id=dialog_id)
        session.add(message)
        await session.commit()
        await session.refresh(message)
    return message


async def get_messages_for_dialog(dialog_id: int):
    """Получение сообщений для диалога"""
    async with async_session() as session:
        messages = await session.execute(select(Message).options(selectinload(Message.sender)).filter_by(dialog_id=dialog_id))
        messages = messages.scalars().all()
    return messages
