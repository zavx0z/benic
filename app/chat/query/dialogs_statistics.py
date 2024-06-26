from typing import List, Optional

from sqlalchemy import select, func, and_

from chat.models.dialog import Dialog, DialogParticipant
from messages.models.message import Message, MessageReaders
from chat.schema.dialog import DialogStatistic
from shared.db import async_session


async def get_dialog_percipient_ids(dialog_id: int) -> [Optional[int]]:
    async with async_session() as session:
        result = await session.execute(
            select(DialogParticipant.user_id).where(DialogParticipant.dialog_id == dialog_id)
        )
        dialog = result.fetchall()
        return [i[0] for i in dialog]


""" Общее количество сообщений для каждого диалога.
Используется функция count для подсчета количества сообщений в каждом диалоге.
"""
all_messages = (  # общее количество сообщений для каждого диалога
    select(
        Message.dialog_id,
        func.count(Message.id).over(partition_by=Message.dialog_id).label('count'),
    )
).alias('all_messages')
# --------------------------------------------------------------------------------------------------------------------
""" Последнее сообщение для каждого диалога. 
Используется функция row_number для нумерации сообщений в каждом диалоге в порядке убывания даты создания, 
чтобы выбрать последнее сообщение.
"""
last_message = (
    select(
        Message.dialog_id,
        Message.sender_id,
        Message.text,
        Message.created_at,
        func.row_number().over(partition_by=Message.dialog_id, order_by=Message.created_at.desc()).label('row_num'),
    )
).alias('last_message')


async def get_dialog_statistics(dialog_id: int, user_id: int) -> DialogStatistic:
    """Получение статистики для заданного диалога."""
    async with async_session() as session:
        # --------------------------------------------------------------------------------------------------------------------
        """ Количество непрочитанных сообщений для каждого диалога.
        Используется функция count для подсчета количества сообщений в каждом диалоге,
        отправленных не заданным пользователем 
        и которые не были прочитаны заданным пользователем.
        """
        unread_messages = (  # количество непрочитанных сообщений для каждого диалога
            select(
                Message.dialog_id,
                func.count(Message.id).over(partition_by=Message.dialog_id).label('count')
            )
            .where(Message.sender_id != user_id)
            .where(Message.id.notin_(select(MessageReaders.message_id).where(MessageReaders.user_id == user_id)))
        ).alias('unread_messages')
        # --------------------------------------------------------------------------------------------------------------------
        """ Объединяет данные из трех подзапросов и получает статистику по каждому диалогу.
        - Ограничивает результат только диалогами, в которых участвует пользователь.        
        - Группируется по Dialog.id, чтобы получить уникальную статистику для каждого диалога.
        """
        dialogs = (
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
            .join(unread_messages, unread_messages.c.dialog_id == Dialog.id, isouter=True)
            .join(last_message, and_(last_message.c.dialog_id == Dialog.id, last_message.c.row_num == 1), isouter=True)
            .where(Dialog.id == dialog_id)
            .group_by(
                Dialog.id,
                all_messages.c.count,
                unread_messages.c.count,
                last_message.c.text,
                last_message.c.created_at,
                last_message.c.sender_id
            )
        ).alias('dialog')
        # --------------------------------------------------------------------------------------------------------------------
        result = await session.execute(select(
            dialogs.c.id.label('dialog_id'),  # ID диалога
            dialogs.c.name.label('dialog_name'),  # название диалога
            dialogs.c.owner_id,  # владелец диалога
            dialogs.c.all_messages_count,  # количество всех сообщений в диалоге.
            dialogs.c.unread_messages_count,  # количество непрочитанных сообщений в диалоге.
            dialogs.c.last_message_text,  # текст последнего сообщения в диалоге.
            dialogs.c.last_message_time,  # время создания последнего сообщения в диалоге.
            dialogs.c.last_message_sender_id  # идентификатор отправителя последнего сообщения.
        ))
        # --------------------------------------------------------------------------------------------------------------------
        result = result.fetchone()
        return DialogStatistic(
            id=result.dialog_id,
            name=result.dialog_name,
            ownerId=result.owner_id,
            totalMessages=result.all_messages_count,
            unreadMessages=result.unread_messages_count if result.unread_messages_count else 0,
            lastMessageText=result.last_message_text,
            lastMessageTime=result.last_message_time.isoformat() if result.last_message_time else None,
            lastMessageSenderId=result.last_message_sender_id,
            participants=await get_dialog_percipient_ids(result.dialog_id)
        )


# todo добавить свой диалог тоже
async def get_user_dialogs_statistics(user_id: int) -> List[DialogStatistic]:
    """Получение статистики по диалогам пользователя.

    :param int user_id: Пользователь, для которого запрашиваются все диалоги, где он является участником.
    :return List[DialogStatistic]: Список объектов DialogStatistic, содержащих статистику по каждому диалогу пользователя.
    """
    async with async_session() as session:
        # --------------------------------------------------------------------------------------------------------------------
        """ Количество непрочитанных сообщений для каждого диалога.
        Используется функция count для подсчета количества сообщений в каждом диалоге,
        отправленных не заданным пользователем 
        и которые не были прочитаны заданным пользователем.
        """
        unread_messages = (  # количество непрочитанных сообщений для каждого диалога
            select(
                Message.dialog_id,
                func.count(Message.id).over(partition_by=Message.dialog_id).label('count')
            )
            .where(Message.sender_id != user_id)
            .where(Message.id.notin_(select(MessageReaders.message_id).where(MessageReaders.user_id == user_id)))
        ).alias('unread_messages')
        # --------------------------------------------------------------------------------------------------------------------
        """ Объединяет данные из трех подзапросов и получает статистику по каждому диалогу.
        - Ограничивает результат только диалогами, в которых участвует пользователь.        
        - Группируется по Dialog.id, чтобы получить уникальную статистику для каждого диалога.
        """
        dialogs = (
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
            .join(unread_messages, unread_messages.c.dialog_id == Dialog.id, isouter=True)
            .join(last_message, and_(last_message.c.dialog_id == Dialog.id, last_message.c.row_num == 1), isouter=True)
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
        # --------------------------------------------------------------------------------------------------------------------
        result = await session.execute(select(
            dialogs.c.id.label('dialog_id'),       # ID диалога
            dialogs.c.name.label('dialog_name'),   # название диалога
            dialogs.c.owner_id,                    # владелец диалога
            dialogs.c.all_messages_count,          # количество всех сообщений в диалоге.
            dialogs.c.unread_messages_count,       # количество непрочитанных сообщений в диалоге.
            dialogs.c.last_message_text,           # текст последнего сообщения в диалоге.
            dialogs.c.last_message_time,           # время создания последнего сообщения в диалоге.
            dialogs.c.last_message_sender_id       # идентификатор отправителя последнего сообщения.
        ))
        # --------------------------------------------------------------------------------------------------------------------
        result = result.fetchall()
        return [DialogStatistic(
            id=row.dialog_id,
            name=row.dialog_name,
            ownerId=row.owner_id,
            totalMessages=row.all_messages_count,
            unreadMessages=row.unread_messages_count if row.unread_messages_count else 0,
            lastMessageText=row.last_message_text,
            lastMessageTime=row.last_message_time.isoformat() if row.last_message_time else None,
            lastMessageSenderId=row.last_message_sender_id,
            participants=await get_dialog_percipient_ids(row.dialog_id)
        ) for row in result]
