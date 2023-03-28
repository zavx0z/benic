import logging

from chat.actions import JOIN, LEAVE, READ, WRITE, UPDATE
from chat.channels import CHANNEL_DIALOG, STATIC_DIALOG, DYNAMIC_DIALOG
from chat.crud.dialog import get_dialog_by_id
from chat.crud.message import create_message
from chat.query.insert import set_messages_read
from chat.query.select import get_messages_for_dialog
from chat.schema import ChatPayload
from chat.schema.message import MessageResponse, MessageInfo
from chat.socketio import send_admin_is_first_message_support_dialog
from shared.socketio.connect import sio

logger = logging.getLogger('sio')


@sio.on(CHANNEL_DIALOG)
async def channel_dialog(sid: str, payload: ChatPayload):  # todo: передавать id последнего сообщения
    payload = ChatPayload(**payload)
    user = await sio.get_session(sid)
    dialog_id = payload.data.get('dialogId')
    DYNAMIC = DYNAMIC_DIALOG(dialog_id)
    STATIC = STATIC_DIALOG(dialog_id)

    if JOIN == payload.action:
        messages = await get_messages_for_dialog(dialog_id, user.id)
        sio.enter_room(sid, DYNAMIC)
        await sio.emit(CHANNEL_DIALOG, {
            "action": payload.action,
            "data": {
                "dialogId": dialog_id,
                "messages": [dict(i) for i in messages]
            }}, room=DYNAMIC)
        logger.info(payload.action, DYNAMIC, user.username)
    elif LEAVE == payload.action:
        sio.leave_room(sid, DYNAMIC)
        logger.info(payload.action, DYNAMIC, user.username)
    elif READ == payload.action:  # Установка статуса ПРОЧИТАНО для сообщений отправителя
        message_ids = payload.data.get('messageIds')
        reader_ids = await set_messages_read(user.id, message_ids)
        if len(reader_ids):
            await sio.emit(CHANNEL_DIALOG, {
                "action": payload.action,
                "data": {
                    "dialogId": dialog_id,
                    "messageIds": message_ids
                }}, room=DYNAMIC)
            logger.info(payload.action, DYNAMIC, user.username, extra={'action': len(reader_ids)})
    elif WRITE == payload.action:
        """Отправка сообщения.
        - если сообщение от пользователя и оно первое в диалоге, подключаем админов
        - детально тем кто в текущий момент в диалоге
            1. собеседникам в диалоге
            2. себе (для подтверждения получения и обновления времени и id сообщения/отправитель может быть и на других устройствах под другим sid)
        - уведомление всем кто участвует в диалоге (для установки последнего сообщения и увеличения счетчика)
        """
        text = payload.data.get("text")
        dialog = await get_dialog_by_id(dialog_id)
        if 'subscribe' == dialog.name and not user.is_superuser:
            await send_admin_is_first_message_support_dialog(user, dialog_id)
        message = await create_message(text=text, sender_id=user.id, dialog_id=dialog.id)
        await sio.emit(CHANNEL_DIALOG, {
            'action': payload.action,
            "data": {
                "dialogId": dialog.id,
                "message": dict(MessageResponse(
                    id=message.id,
                    senderId=message.sender_id,
                    created=message.created_at.isoformat(),
                    text=message.text,
                    read=False))
            }}, room=DYNAMIC)
        logger.info(payload.action, DYNAMIC, user.username)
        await sio.emit(CHANNEL_DIALOG, {
            'action': UPDATE,
            "data": {
                "dialogId": dialog.id,
                "message": dict(MessageInfo(
                    lastMessageSenderId=message.sender_id,
                    lastMessageTime=message.created_at.isoformat(),
                    lastMessageText=message.text[:min(len(message.text), 40)]
                ))
            }}, room=STATIC)
        logger.info(payload.action, STATIC, user.username)
