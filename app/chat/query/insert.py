from typing import List

from sqlalchemy import select, insert

from chat.models.message import MessageReaders
from shared.db import async_session


async def set_messages_read(user_id: int, message_ids: List[int]) -> List[int]:
    """Установка записей о прочтении нескольких сообщений пользователем

        Функция создает записи в таблице MessageReaders, указывая user_id, message_id и текущее время как read_time,
        только в том случае, если для данного сообщения и пользователя в базе данных ещё не существует записи о прочтении.
        Если запись успешно добавлена, то возвращается список добавленных сообщений.

        :param user_id: ID пользователя
        :type user_id: int
        :param message_ids: Список ID сообщений
        :type message_ids: List[int]
        :return: Список ID сообщений, на которые были успешно добавлены записи о прочтении
        :rtype: List[int]
        :raises sqlalchemy.exc.SQLAlchemyError: Если произошла ошибка при работе с базой данных
    """
    added_message_ids = []
    async with async_session() as session:
        stmts = []
        for message_id in message_ids:
            stmt = select(MessageReaders).where((MessageReaders.message_id == message_id) & (MessageReaders.user_id == user_id))
            result = await session.execute(stmt)
            message_read = result.scalar_one_or_none()
            if message_read is None:
                stmts.append({"user_id": user_id, "message_id": message_id})
                added_message_ids.append(message_id)
        if stmts:
            await session.execute(insert(MessageReaders), stmts)
            await session.commit()
    return added_message_ids
