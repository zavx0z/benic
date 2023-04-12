import logging
from typing import List

from chat.actions import UPDATE, WRITE
from chat.actions.support import emit_admin_update_chat
from chat.channels import CHANNEL_DIALOG, DYNAMIC_DIALOG, STATIC_DIALOG, CHANNEL_SUPPORT
from chat.crud.dialog import get_dialog_by_id, get_messages_count
from chat.crud.message import create_message
from messages.models.message import Message
from messages.schema.message import MessageResponse, MessageInfo
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


async def send_msg_info_to_dialog_participants(user: SessionUser, dialog_id: int, message: Message):
    """Рассылка информации о переданном сообщении всем участникам диалога

    (для установки последнего сообщения и увеличения счетчика)
    """
    room = STATIC_DIALOG(dialog_id)
    data_info = MessageInfo(
        lastMessageSenderId=message.sender_id,
        lastMessageTime=message.created_at.isoformat(),
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


async def send_msg_detail_to_dialog_participants(user: SessionUser, dialog_id: int, message: Message):
    """ Рассылка переданного сообщения участникам которые в текущий момент находятся в диалоге

    1. Собеседникам в диалоге
    2. Себе (для подтверждения получения и обновления времени и id сообщения/отправитель может быть и на других устройствах под другим sid)
    """
    room = DYNAMIC_DIALOG(dialog_id)
    data_message = MessageResponse(
        id=message.id,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text,
        read=False
    )
    await sio.emit(event=CHANNEL_DIALOG, room=room, data={
        'action': WRITE,
        "data": {
            "dialogId": dialog_id,
            "message": dict(data_message)
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

    if CHANNEL_SUPPORT == dialog.name and user.role.value <= Role.developer.value:
        count_messages = await get_messages_count(dialog_id)
        if count_messages == 2:
            await emit_admin_update_chat(user.id, dialog.id, message)
            await send_msg_detail_to_dialog_participants(user, dialog_id, message)
            return
    await send_msg_detail_to_dialog_participants(user, dialog_id, message)
    await send_msg_info_to_dialog_participants(user, dialog_id, message)