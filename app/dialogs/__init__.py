import logging

from chat.actions import JOIN, LEAVE, READ, WRITE, JOIN_STATIC
from chat.channels import CHANNEL_DIALOG
from chat.query.select import get_messages_for_dialog
from chat.schema import ChatPayload
from dialogs.actions.connect import after_connect
from dialogs.actions.join import join_dialog_dynamic_room, join_dialog_static_room
from dialogs.actions.leave import leave_dialog_dynamic_room
from dialogs.actions.read import read
from dialogs.actions.write import receiving_message
from events import async_event_manager, SIO_CONNECT, DB_CREATE_USER
from shared.socketio import sio
from .hooks import after_create_user

logger = logging.getLogger('sio')

# async_event_manager.subscribe(SIO_DISCONNECT, leave_static_dialog)

async_event_manager.subscribe(SIO_CONNECT, after_connect)
async_event_manager.subscribe(DB_CREATE_USER, after_create_user)


@sio.on(CHANNEL_DIALOG)
async def channel_dialog(sid: str, payload: ChatPayload):  # todo: передавать id последнего сообщения
    payload = ChatPayload(**payload)
    user = await sio.get_session(sid)
    dialog_id = payload.data.get('dialogId')
    if JOIN == payload.action:
        join_dialog_dynamic_room(user, dialog_id)
        messages = await get_messages_for_dialog(dialog_id, user.id)
        return [dict(i) for i in messages]
    elif LEAVE == payload.action:
        leave_dialog_dynamic_room(user, dialog_id)
    elif READ == payload.action:  # Установка статуса ПРОЧИТАНО для сообщений отправителя
        await read(user, dialog_id, message_ids=payload.data.get('messageIds'))
    elif WRITE == payload.action:
        message = await receiving_message(user, dialog_id, text=payload.data.get("text"))
        return dict(message)
    elif JOIN_STATIC == payload.action:
        join_dialog_static_room(user, dialog_id)
