from typing import List

from sqlalchemy import func, select, and_

from chat.models.dialog import Dialog, DialogParticipant
from chat.models.message import Message
from chat.models.message import MessageReaders
from chat.schema.dialog import DialogStatistic
from chat.schema.message import MessageResponse
from shared.db import async_session


async def get_user_dialog_statistics(user_id: int) -> List[DialogStatistic]:
    async with async_session() as session:
        all_messages = (  # общее количество сообщений для каждого диалога
            select(
                Message.dialog_id,
                func.count(Message.id).over(partition_by=Message.dialog_id).label('count'),
            )
        ).alias('all_messages')
        unread_messages = (  # количество непрочитанных сообщений для каждого диалога
            select(
                Message.dialog_id,
                func.count(Message.id).over(partition_by=Message.dialog_id).label('count')
            )
            .where(Message.sender_id != user_id)
            .where(Message.id.notin_(select(MessageReaders.message_id).where(MessageReaders.user_id == user_id)))
        ).alias('unread_messages')
        last_message = (  # последнее сообщение для каждого диалога
            select(
                Message.dialog_id,
                Message.sender_id,
                Message.text,
                Message.created_at,
                func.row_number().over(partition_by=Message.dialog_id, order_by=Message.created_at.desc()).label('row_num'),
            )
        ).alias('last_message')
        dialogs = (  # объединяет данные из трех подзапросов и получает статистику по каждому диалогу
            select(
                Dialog.id,
                Dialog.name,
                Dialog.owner_id,
                all_messages.c.count.label('all_messages_count'),
                unread_messages.c.count.label('unread_messages_count'),
                last_message.c.text.label('last_message_text'),
                last_message.c.created_at.label('last_message_time'),
                last_message.c.sender_id.label('last_message_sender_id'),
            )
            .join(all_messages, all_messages.c.dialog_id == Dialog.id)
            .join(unread_messages, unread_messages.c.dialog_id == Dialog.id)
            .join(last_message, and_(last_message.c.dialog_id == Dialog.id, last_message.c.row_num == 1))
            .where(Dialog.id.in_(select(DialogParticipant.dialog_id).where(DialogParticipant.user_id == user_id)))
            .group_by(
                Dialog.id,
                all_messages.c.count,
                unread_messages.c.count,
                last_message.c.text,
                last_message.c.created_at,
                last_message.c.sender_id
            )
        ).alias('dialog')
        result = await session.execute(select(
            dialogs.c.id.label('dialog_id'),
            dialogs.c.name.label('dialog_name'),
            dialogs.c.owner_id,
            dialogs.c.all_messages_count,
            dialogs.c.unread_messages_count,
            dialogs.c.last_message_text,
            dialogs.c.last_message_time,
            dialogs.c.last_message_sender_id
        ))
        return [DialogStatistic(
            dialogId=row.dialog_id,
            dialogName=row.dialog_name,
            ownerId=row.owner_id,
            totalMessages=row.all_messages_count,
            unreadMessages=row.unread_messages_count,
            lastMessageText=row.last_message_text,
            lastMessageTime=row.last_message_time.isoformat() if row.last_message_time else None,
            lastMessageSenderId=row.last_message_sender_id,
        ) for row in result.fetchall()]


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
