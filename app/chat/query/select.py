from typing import List

from sqlalchemy import func, and_
from sqlalchemy import select

from chat.models.dialog import DialogParticipant, Dialog
from chat.models.message import Message
from chat.models.message import MessageReaders
from chat.schema.dialog import DialogStatistic
from chat.schema.message import MessageResponse
from shared.db import async_session


async def get_user_dialog_statistics(user_id: int) -> List[DialogStatistic]:
    """Получение статистики по диалогам, в которых состоит пользователь с заданным user_id"""
    async with async_session() as session:
        subquery = (
            select(
                Message.dialog_id,
                func.count(Message.id).label('unread_messages'))
            .join(MessageReaders, and_(MessageReaders.message_id == Message.id, MessageReaders.user_id != user_id), isouter=True)
            .where(Message.sender_id != user_id)
            .group_by(Message.dialog_id)
            .subquery()
        )
        counts = await session.execute(
            select(
                Dialog.id,
                Dialog.name,
                func.count(Message.id).label('total_messages'),
                func.coalesce(subquery.c.unread_messages, 0).label('unread_messages')
            )
            .join(DialogParticipant, DialogParticipant.dialog_id == Dialog.id)
            .join(Dialog.messages)
            .outerjoin(subquery, subquery.c.dialog_id == Dialog.id)
            .where(DialogParticipant.user_id == user_id)
            .group_by(Dialog.id, subquery.c.unread_messages)
        )
        result = counts.fetchall()
        return [DialogStatistic(
            dialogId=dialog_id,
            dialogName=dialog_name,
            totalMessages=total_messages,
            unreadMessages=unread_messages
        ) for dialog_id, dialog_name, total_messages, unread_messages in result]


async def get_messages_for_dialog(dialog_id: int, user_id: int):
    """Получение сообщений для диалога и информации о том, прочитал ли пользователь сообщение

    SQL запрос, который:
    1. объединяет таблицы Message и MessageReaders по полю id и фильтрует результаты по dialog_id и user_id.
    2. создает список MessageResponse объектов, используя данные из результатов SQL запроса и проверяя, было ли сообщение прочитано пользователем user_id.
    Проверка на прочтение:
     - Если read_time в MessageReaders таблице для данного сообщения и данного пользователя не существует, то мы предполагаем, что сообщение не было прочитано.
     - Если sender_id в Message таблице не равен user_id, то мы также предполагаем, что сообщение было прочитано.
     - В противном случае сообщение не было прочитано.
    """
    async with async_session() as session:
        stmt = (
            select(Message.id,
                   Message.text,
                   Message.created_at,
                   Message.sender_id,
                   MessageReaders.read_time)
            .join(MessageReaders, and_(Message.id == MessageReaders.message_id, MessageReaders.user_id == user_id), isouter=True)
            .filter(Message.dialog_id == dialog_id)
            .order_by(Message.created_at)
        )
        result = await session.execute(stmt)
        messages = result.fetchall()
        return [MessageResponse(
            id=m.id,
            senderId=m.sender_id,
            created=m.created_at.isoformat(),
            text=m.text,
            read=bool(m.read_time is not None and m.sender_id != user_id)
        ) for m in messages]
