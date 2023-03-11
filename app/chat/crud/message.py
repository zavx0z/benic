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


# async def get_messages_for_client(user_id: int, dialog_name: str):
#     """Получение сообщений для диалога пользователя"""
#     async with async_session() as session:
#         # Find the dialog by name and owner user ID
#         dialog = await session.execute(
#             select(Dialog)
#             .options(selectinload(Dialog.owner), selectinload(Dialog.participants).selectinload(DialogParticipant.user))
#             .where(and_(Dialog.name == dialog_name, Dialog.owner_id == user_id))
#         ).scalar_one_or_none()
#         if dialog is None:
#             # Dialog not found for the user
#             return []
#         # Retrieve messages for the dialog
#         messages = await session.execute(
#             select(Message)
#             .options(selectinload(Message.sender))
#             .filter_by(dialog_id=dialog.id)
#         ).scalars().all()
#         return messages
