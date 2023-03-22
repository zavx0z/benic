from pydantic import BaseModel


class DialogStatistic(BaseModel):
    """ Модель для представления статистики по диалогам.

    :param int id: ID диалога.
    :param str name: Название диалога.
    :param int totalMessages: Общее количество сообщений в диалоге.
    :param int unreadMessages: Количество непрочитанных сообщений в диалоге.
    :param int ownerId: ID владельца диалога.
    :param str lastMessageText: Текст последнего сообщения в диалоге.
    :param str lastMessageTime: Время отправки последнего сообщения.
    :param str lastMessageSenderId: ID пользователя отправившего сообщение.
    """
    id: int
    name: str
    ownerId: int
    totalMessages: int
    unreadMessages: int
    lastMessageText: str
    lastMessageTime: str
    lastMessageSenderId: int


class DialogChatDB(BaseModel):
    """ Модель для представления в чате.

    :param int id: ID диалога.
    :param str name: Название диалога.
    :param int ownerId: ID владельца диалога.
    """
    id: int
    name: str
    ownerId: int
