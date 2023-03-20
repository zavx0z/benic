from typing import List, Dict

import numpy as np
import pandas as pd
from sqlalchemy import and_
from sqlalchemy import select

from chat.crud.dialog import get_dialog_last_message, get_unread_message_count_for_dialogs, get_all_message_count_for_dialogs, get_dialogs_by_user_id
from chat.models.message import Message
from chat.models.message import MessageReaders
from chat.schema.dialog import DialogStatistic
from chat.schema.message import MessageResponse
from shared.db import async_session


async def get_user_dialog_statistics(user_id: int) -> List[Dict]:
    """
    Получает статистику диалогов пользователя.

    :param user_id: ID пользователя.
    :return: Список объектов DialogStatistics.
    """
    async with async_session() as session:
        dialogs = await get_dialogs_by_user_id(session, user_id)
        dialog_ids = [i[0] for i in dialogs]
        all_messages_count = await get_all_message_count_for_dialogs(session, dialog_ids)
        unread_messages_count = await get_unread_message_count_for_dialogs(session, dialog_ids, user_id)
        last_messages = await get_dialog_last_message(session, dialog_ids)

        dialogs = pd.DataFrame(dialogs, columns=['dialogId', 'ownerId', 'ownerName']).set_index('dialogId')
        all_messages_count = pd.DataFrame(all_messages_count, columns=['dialogId', 'totalMessages']).set_index('dialogId')
        unread_messages_count = pd.DataFrame(unread_messages_count, columns=['dialogId', 'unreadMessages']).set_index('dialogId')
        last_messages = pd.DataFrame(last_messages, columns=['dialogId', 'lastMessageText', 'lastMessageTime']).set_index('dialogId')
        last_messages.lastMessageTime = last_messages.lastMessageTime.apply(lambda value: value.isoformat())
        result = pd.concat([dialogs, all_messages_count, unread_messages_count, last_messages], axis=1)
        result.reset_index(inplace=True)
        result.replace(np.nan, None, inplace=True)
        return result.to_dict(orient='records')


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
