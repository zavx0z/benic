import logging

from chat.channels import CHANNEL_SUPPORT
from chat.crud.dialog import create_dialog
from chat.crud.message import create_message
from config import ADMIN_ID

logger = logging.getLogger('sio')


async def create_support_dialog_and_send_welcome_message(sio, user_id: int, welcome_text):
    """ Создает диалог между пользователем и администратором.
        Создает приветственное сообщение.
    """
    # создаем диалог поддержки
    dialog = await create_dialog(CHANNEL_SUPPORT, user_id, [user_id, ADMIN_ID])
    # Сохраняем приветственное сообщение от User.id == 1 (zavx0z) в диалог поддержки
    message = await create_message(
        text=welcome_text,
        dialog_id=dialog.id,
        sender_id=1
    )
    # """Для ВСЕХ участников диалога рассылка на обновление диалогов пользователя (добавление диалога админу)
    #     (канал статичного типа подключения)
    # - Последний отправитель (zavx0z)
    # - Время последнего сообщения
    # - Текст последнего сообщения
    # - Кто отправил
    # - ID диалога
    # ** ВСЕХ - это значит ВСЕ кто залогинен
    # """
    # await sio.emit(CHANNEL_DIALOG, {
    #     'action': UPDATE,
    #     "data": {
    #         "dialogId": dialog.id,
    #         "message": dict(MessageInfo(
    #             lastMessageSenderId=message.sender_id,
    #             lastMessageTime=message.created_at.isoformat(),
    #             lastMessageText=message.text[:min(len(message.text), 40)]
    #         ))
    #     }}, room=STATIC_DIALOG(dialog.id))
    # logger.info(UPDATE, STATIC_DIALOG(dialog.id), user.username)
    # """ Отправка сообщения на запись ПОДКЛЮЧЕННЫМ пользователям к диалогу
    #     (канал динамического типа подключения)
    # - администратор получает данные на подтверждение получения сообщения с актуальным id и временем создания сообщения
    # - Пользователь получает сообщение в диалог поддержки
    # ** ПОДКЛЮЧЕННЫЕ - это значит находящиеся в приложении на странице диалога
    # """
    # DYNAMIC = DYNAMIC_DIALOG(dialog.id)
    # sio.enter_room(sid, DYNAMIC)
    # Отправляется сообщение о создании диалога в динамическую комнату.
    # await sio.emit(CHANNEL_DIALOG, {
    #     'action': action.WRITE,
    #     "data": {
    #         "dialogId": dialog.id,
    #         "message": dict(MessageResponse(
    #             id=message.id,
    #             senderId=message.sender_id,
    #             created=message.created_at.isoformat(),
    #             text=message.text,
    #             read=False))
    #     }}, room=DYNAMIC_DIALOG(dialog.id))
