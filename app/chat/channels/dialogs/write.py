import logging

from chat.actions import UPDATE, WRITE
from chat.channels import CHANNEL_DIALOG, DYNAMIC_DIALOG, STATIC_DIALOG
from chat.crud.dialog import get_dialog_by_id
from chat.crud.message import create_message
from chat.schema.message import MessageResponse, MessageInfo
from chat.socketio import send_admin_is_first_message_support_dialog
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def write_message(user, dialog_id, text):
    """Отправка сообщения.
    - если сообщение от пользователя и оно первое в диалоге, подключаем админов
    - детально тем кто в текущий момент в диалоге
        1. собеседникам в диалоге
        2. себе (для подтверждения получения и обновления времени и id сообщения/отправитель может быть и на других устройствах под другим sid)
    - уведомление всем кто участвует в диалоге (для установки последнего сообщения и увеличения счетчика)
    """
    dialog = await get_dialog_by_id(dialog_id)
    if 'subscribe' == dialog.name and not user.is_superuser:
        await send_admin_is_first_message_support_dialog(user, dialog_id)

    message = await create_message(text=text, sender_id=user.id, dialog_id=dialog.id)

    DYNAMIC = DYNAMIC_DIALOG(dialog_id)
    STATIC = STATIC_DIALOG(dialog_id)

    await sio.emit(
        event=CHANNEL_DIALOG,
        room=DYNAMIC,
        data={
            'action': WRITE,
            "data": {
                "dialogId": dialog.id,
                "message": dict(MessageResponse(
                    id=message.id,
                    senderId=message.sender_id,
                    created=message.created_at.isoformat(),
                    text=message.text,
                    read=False))
            }
        })
    logger.info(user.id, user.username, user.sid, WRITE, CHANNEL_DIALOG, DYNAMIC)

    await sio.emit(
        event=CHANNEL_DIALOG,
        room=STATIC,
        data={
            'action': UPDATE,
            "data": {
                "dialogId": dialog.id,
                "message": dict(MessageInfo(
                    lastMessageSenderId=message.sender_id,
                    lastMessageTime=message.created_at.isoformat(),
                    lastMessageText=message.text[:min(len(message.text), 40)]))
            }
        })
    logger.info(user.id, user.username, user.sid, UPDATE, CHANNEL_DIALOG, STATIC)
