from typing import Optional, Union

from pydantic import BaseModel

from chat.const import DIALOG_NAME
from chat.crud.dialog import get_dialogs_by_user_id_and_name
from chat.crud.message import create_message
from chat.query.dialogs_statistics import get_user_dialog_statistics
from chat.query.insert import set_messages_read
from chat.query.select import get_messages_for_dialog, get_users
from chat.schema import MessageRequest
from chat.schema.clientresponse import ClientResponse
from chat.schema.message import MessageResponse
from shared.socketio import sio


@sio.on('support')
async def handle_message(sid: str, data: MessageRequest):
    data = MessageRequest(**data)
    user = await sio.get_session(sid)
    dialogs = await get_dialogs_by_user_id_and_name(data.ownerId, DIALOG_NAME)
    dialog = dialogs[0]
    # рассылка админам при первом сообщении
    if not user.is_superuser:
        count_messages = await dialog.get_messages_count()
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog.id)))
    message = await create_message(text=data.text, sender_id=user.id, dialog_id=dialog.id)
    print(f"send dialog {dialog.id}")
    await sio.emit('support', dict(MessageResponse(
        id=message.id,
        ownerId=data.ownerId,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text,
    )), room=dialog.id)


@sio.on('subscribeDialog')
async def subscribe_dialog(sid: str, dialog_id: int):  # todo: передавать id последнего сообщения
    dialog_room = f"dialog_{dialog_id}"
    user = await sio.get_session(sid)
    print(f"Пользователь {user.username} в диалоге {dialog_room}")
    sio.enter_room(sid, dialog_room)
    messages = await get_messages_for_dialog(dialog_id, user.id)
    await sio.emit('subscribeDialog', {"dialogId": dialog_id, "messages": [dict(i) for i in messages]}, room=dialog_room)


@sio.on('unSubscribeDialog')
async def subscribe_dialog(sid: str, dialog_id: int):
    dialog_room = f"dialog_{dialog_id}"
    user = await sio.get_session(sid)
    print(f"Пользователь {user.username} покинул диалог {dialog_room}")
    sio.leave_room(sid, dialog_room)


class Chat(BaseModel):
    action: str
    data: Optional[Union[dict, int, list]]


@sio.on('chat')
async def read_message(sid: str, payload: Chat):
    user = await sio.get_session(sid)
    payload = Chat(**payload)
    if payload.action == 'init':
        result = await get_user_dialog_statistics(user.id)
        await sio.emit('chat', {
            "action": 'init',
            "data": [dict(item) for item in result]
        }, room=sid)
    elif payload.action == 'read':
        dialog_id = payload.data.get('dialogId')
        message_ids = payload.data.get('messageIds')
        added_ids = await set_messages_read(user.id, message_ids)
        if len(added_ids):
            await sio.emit('chat', {
                "action": payload.action,
                "data": {"dialogId": dialog_id, "messageIds": message_ids}
            }, room=sid)
    elif payload.action == 'users':
        result = await get_users(payload.data)
        await sio.emit('users', [dict(item) for item in result], room=sid)


@sio.on("joinDialog")
async def join_dialog(sid, dialog_id):
    print(f"{sid} enter dialog {dialog_id}")
    sio.enter_room(sid, dialog_id)
