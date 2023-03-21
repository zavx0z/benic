from typing import List

from sqlalchemy import func, select, text, and_

from auth.models import User
from chat.models.dialog import Dialog, DialogParticipant
from chat.models.message import Message
from chat.models.message import MessageReaders
from chat.schema.dialog import DialogStatistic
from chat.schema.message import MessageResponse
from shared.db import async_session


async def get_user_dialog_statistics(user_id: int) -> List[DialogStatistic]:
    async with async_session() as session:
        subquery_all_messages = (
            select(
                Message.dialog_id,
                func.count(Message.id).over(partition_by=Message.dialog_id).label('count'),
            )
            .where(Message.dialog_id.in_(select(DialogParticipant.dialog_id).where(DialogParticipant.user_id == user_id)))
            .alias('all_messages_subquery')
        )
        subquery_unread_messages = (
            select(
                Message.dialog_id,
                func.count(Message.id).over(partition_by=Message.dialog_id).label('count')
            )
            .where(Message.sender_id != user_id)
            .where(Message.id.notin_(select(MessageReaders.message_id).where(MessageReaders.user_id == user_id)))
            .where(Message.dialog_id.in_(select(DialogParticipant.dialog_id).where(DialogParticipant.user_id == user_id)))
            .alias('unread_messages_subquery')
        )
        subquery_last_message = (
            select(
                Message.dialog_id,
                Message.text,
                Message.created_at,
                func.row_number().over(partition_by=Message.dialog_id, order_by=Message.created_at.desc()).label('row_num')
            )
            .where(Message.dialog_id.in_(select(DialogParticipant.dialog_id).where(DialogParticipant.user_id == user_id)))
            .alias('last_message_subquery')
        )
        subquery_dialogs = (
            select(
                Dialog.id,
                Dialog.name,
                Dialog.owner_id,
                User.username,
                subquery_all_messages.c.count.label('all_messages_count'),
                subquery_unread_messages.c.count.label('unread_messages_count'),
                subquery_last_message.c.text.label('last_message_text'),
                subquery_last_message.c.created_at.label('last_message_time')
            )
            .select_from(Dialog)
            .join(User, User.id == Dialog.owner_id)
            .join(subquery_all_messages, subquery_all_messages.c.dialog_id == Dialog.id)
            .join(subquery_unread_messages, subquery_unread_messages.c.dialog_id == Dialog.id)
            .join(subquery_last_message, text('last_message_subquery.row_num = 1 and last_message_subquery.dialog_id = dialog.id'))
            .where(Dialog.id.in_(select(DialogParticipant.dialog_id).where(DialogParticipant.user_id == user_id)))
            .group_by(
                Dialog.id,
                User.username,
                subquery_all_messages.c.count,
                subquery_unread_messages.c.count,
                subquery_last_message.c.text,
                subquery_last_message.c.created_at
            )
            .alias('dialog_subquery')
        )
        query = select(
            subquery_dialogs.c.id.label('dialog_id'),
            subquery_dialogs.c.name.label('dialog_name'),
            subquery_dialogs.c.owner_id,
            subquery_dialogs.c.username.label('owner_name'),
            subquery_dialogs.c.all_messages_count,
            subquery_dialogs.c.unread_messages_count,
            subquery_dialogs.c.last_message_text,
            subquery_dialogs.c.last_message_time
        )
        rows = await session.execute(query)
        result = rows.fetchall()
        return [DialogStatistic(
            dialogId=row[0],
            dialogName=row[1],
            ownerId=row[2],
            ownerName=row[3],
            totalMessages=row[4],
            unreadMessages=row[5],
            lastMessageText=row[6],
            lastMessageTime=row[7].isoformat() if row[7] else None,
        ) for row in result]


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
        result = await session.execute(
            select(Message.id,
                   Message.text,
                   Message.created_at,
                   Message.sender_id,
                   MessageReaders.read_time)
            .join(MessageReaders, and_(Message.id == MessageReaders.message_id, MessageReaders.user_id == user_id), isouter=True)
            .filter(Message.dialog_id == dialog_id)
            .order_by(Message.created_at)
        )
        return [MessageResponse(
            id=m.id,
            senderId=m.sender_id,
            created=m.created_at.isoformat(),
            text=m.text,
            read=bool(m.read_time is not None and m.sender_id != user_id)
        ) for m in result]
