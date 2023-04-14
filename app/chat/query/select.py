from typing import List

from sqlalchemy import select

from clients.schema import DeviceUserChat
from messages.models.message import Message, MessageReaders
from messages.schema.message import MessageResponse
from shared.db import async_session
from sso.models.user import User


async def get_messages_for_dialog(dialog_id: int, user_id: int) -> List[MessageResponse]:
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
            select(
                Message.id,
                Message.text,
                Message.created_at,
                Message.sender_id,
                MessageReaders.read_time.label('read')
            )
            .join(MessageReaders, Message.id == MessageReaders.message_id, isouter=True)
            .filter(Message.dialog_id == dialog_id)
            .order_by(Message.created_at)
        )
        messages = result.mappings()
        return [MessageResponse(**message) for message in messages]


async def get_users(user_idx: List[int]):
    """Получение пользователей
    """
    async with async_session() as session:
        result = await session.execute(
            select(
                User.id,
                User.username,
            )
            .where(User.id.in_(user_idx))
        )
    return [DeviceUserChat(id=i.id, name=i.username) for i in result.fetchall()]


