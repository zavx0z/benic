import logging
from typing import List

from chat.actions import UPDATE, WRITE
from chat.actions.support import emit_admin_update_chat
from chat.channels import CHANNEL_DIALOG, DYNAMIC_DIALOG, STATIC_DIALOG, CHANNEL_SUPPORT
from chat.crud.dialog import get_dialog_by_id, get_messages_count
from chat.crud.message import create_message
from messages.models.message import Message
from messages.schema.message import MessageInfo, MessageResponse
from notifications.tasks import notification_clients_not_currently_in_dialog
from shared.session import SessionUser
from shared.socketio import sio
from sso.models.role import Role

logger = logging.getLogger('action')


async def current_clients_in_dialog(dialog_id: int) -> List[int]:
    room = DYNAMIC_DIALOG(dialog_id)
    online_participants = [await sio.get_session(i[0]) for i in sio.manager.get_participants('/', room)]
    all_clients = list(set(i.device_id for i in online_participants))
    return all_clients


async def emit_message_info_to_dialog_participants(user: SessionUser, dialog_id: int, message: MessageResponse):
    """Рассылка информации о переданном сообщении всем участникам диалога

    (для установки последнего сообщения и увеличения счетчика)
    """
    room = STATIC_DIALOG(dialog_id)
    data_info = MessageInfo(
        lastMessageSenderId=message.senderId,
        lastMessageTime=message.created,
        lastMessageText=message.text[:min(len(message.text), 40)]
    )
    await sio.emit(event=CHANNEL_DIALOG, room=room, data={
        'action': UPDATE,
        "data": {
            "dialogId": dialog_id,
            "message": dict(data_info)
        }})
    current_clients = await current_clients_in_dialog(dialog_id)
    notification_clients_not_currently_in_dialog.send_with_options(kwargs={
        'dialog_id': dialog_id,
        'sender_id': user.id,
        'sender_name': user.username,
        'current_clients': current_clients,
        'message': message.text,
    })
    logger.info(user.id, user.username, user.sid, UPDATE, CHANNEL_DIALOG, room)


async def emit_message_detail_to_dialog_participants(user: SessionUser, dialog_id: int, message: MessageResponse):
    """ Рассылка переданного сообщения участникам которые в текущий момент находятся в диалоге

    1. Собеседникам в диалоге
    2. Себе (для подтверждения получения и обновления времени и id сообщения/отправитель может быть и на других устройствах под другим sid)
    """
    room = DYNAMIC_DIALOG(dialog_id)
    await sio.emit(event=CHANNEL_DIALOG, room=room, skip_sid=user.sid, data={
        'action': WRITE,
        "data": {
            "dialogId": dialog_id,
            "message": dict(message)
        }})
    logger.info(user.id, user.username, user.sid, WRITE, CHANNEL_DIALOG, room)


async def receiving_message(user, dialog_id, text):
    """Прием сообщения.

    - если сообщение от пользователя и это первое сообщение принадлежащее ему - подключаем админов
    - сохранение
    - рассылка информации
    - рассылка сообщения
    """
    dialog = await get_dialog_by_id(dialog_id)
    message = await create_message(text=text, sender_id=user.id, dialog_id=dialog.id)
    message = MessageResponse(**message.__dict__)
    if CHANNEL_SUPPORT == dialog.name and user.role.value <= Role.developer.value:
        count_messages = await get_messages_count(dialog_id)
        if count_messages == 2:
            await emit_admin_update_chat(user.id, dialog.id, message.text, message.created)
            await emit_message_detail_to_dialog_participants(user, dialog_id, message)
            return message
    await emit_message_detail_to_dialog_participants(user, dialog_id, message)
    await emit_message_info_to_dialog_participants(user, dialog_id, message)
    return message
