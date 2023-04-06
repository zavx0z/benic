import logging

from chat.actions import JOIN, LEAVE, READ, WRITE
from chat.channels import CHANNEL_DIALOG
from chat.schema import ChatPayload
from events import async_event_manager, SIO_CONNECT, DB_CREATE_USER
from shared.socketio.connect import sio
from .connect import after_connect
from .get import get_dialog
from .hooks import after_create_user
from .join import join_dialog_dynamic_room
from .leave import leave_dialog_dynamic_room
from .read import read
from .write import receiving_message

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
        await join_dialog_dynamic_room(user, dialog_id)
        await get_dialog(user, dialog_id)
    elif LEAVE == payload.action:
        leave_dialog_dynamic_room(user, dialog_id)
    elif READ == payload.action:  # Установка статуса ПРОЧИТАНО для сообщений отправителя
        await read(user, dialog_id, message_ids=payload.data.get('messageIds'))
    elif WRITE == payload.action:
        await receiving_message(user, dialog_id, text=payload.data.get("text"))
