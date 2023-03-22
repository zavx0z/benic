from typing import Optional, Union, List

from pydantic import BaseModel

from chat.channerls import ROOM_CHANNEL_DIALOG, CHANNEL_DIALOG, CHANNEL_USERS
from chat.crud.dialog import get_dialog_by_id, get_messages_count
from chat.crud.message import create_message
from chat.query.dialogs_statistics import get_user_dialog_statistics
from chat.query.insert import set_messages_read
from chat.query.select import get_messages_for_dialog, get_users_by_dialog_ids
from chat.schema import SessionUser
from chat.schema.clientresponse import ClientResponse
from chat.schema.message import MessageResponse
from shared import action
from shared.socketio import sio


class DialogMessageRequest(BaseModel):
    id: int
    senderId: int
    text: str


@sio.on('message')
async def handle_message(sid: str, data: DialogMessageRequest):
    data = DialogMessageRequest(**data)
    user = await sio.get_session(sid)
    dialog = await get_dialog_by_id(data.id)
    # рассылка админам при первом сообщении
    if not user.is_superuser:
        count_messages = await get_messages_count(dialog.id)
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog.id)))
    message = await create_message(text=data.text, sender_id=user.id, dialog_id=dialog.id)
    print(f"Отправка сообщения в диалог {dialog.id}")
    message = dict(MessageResponse(
        id=message.id,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text,
        read=False
    ))
    # await sio.emit('support', message, room=dialog.id)
    await sio.emit('message', {"dialogId": dialog.id, "message": message}, room=ROOM_CHANNEL_DIALOG(dialog.id))
    await sio.emit(CHANNEL_DIALOG, {"dialogId": dialog.id, "unreadMessages": 1}, room=ROOM_CHANNEL_DIALOG(dialog.id), skip_sid=sid)


class ChatPayload(BaseModel):
    action: str
    data: Optional[Union[dict, int, list]]


GET = 'get'
JOIN = 'join'
UPDATE = 'update'
LEAVE = 'leave'
READ = 'read'
WRITE = 'write'
format_log = lambda action, room, username, param_action=None: print(f"{action.upper():7}{'' if param_action is None else param_action} {room:10} from: {username}")


async def dialog_join(sid: str, dialog_id: int, user_id: int):
    dialog_room = ROOM_CHANNEL_DIALOG(dialog_id)
    messages = await get_messages_for_dialog(dialog_id, user_id)
    sio.enter_room(sid, dialog_room)
    await sio.emit(CHANNEL_DIALOG, {
        "action": action.JOIN,
        "data": {
            "dialogId": dialog_id,
            "messages": [dict(i) for i in messages]
        }
    }, room=dialog_room)


async def dialog_read(sid: str, dialog_id: int, user_id: int, message_ids: List[int]):
    dialog_room = ROOM_CHANNEL_DIALOG(dialog_id)
    reader_ids = await set_messages_read(user_id, message_ids)
    count = len(reader_ids)
    if count:
        await sio.emit(CHANNEL_DIALOG, {
            "action": READ,
            "data": {
                "dialogId": dialog_id,
                "messageIds": message_ids
            }
        }, room=dialog_room)
        return count


async def dialog_write(sid: str, dialog_id: int, message_text: str, user: SessionUser, dialog_room: str):
    dialog = await get_dialog_by_id(dialog_id)
    # рассылка админам при первом сообщении
    if not user.is_superuser:
        count_messages = await get_messages_count(dialog.id)
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog.id)))
    message = await create_message(text=message_text, sender_id=user.id, dialog_id=dialog.id)
    await sio.emit(CHANNEL_DIALOG, {
        'action': WRITE,
        "data": {
            "dialogId": dialog.id,
            "message": dict(MessageResponse(
                id=message.id,
                senderId=message.sender_id,
                created=message.created_at.isoformat(),
                text=message.text,
                read=False))
        }}, room=dialog_room)


@sio.on(CHANNEL_DIALOG)
async def channel_dialog(sid: str, payload: ChatPayload):  # todo: передавать id последнего сообщения
    payload = ChatPayload(**payload)
    user = await sio.get_session(sid)
    if payload.action == JOIN:
        dialog_room = ROOM_CHANNEL_DIALOG(payload.data)
        format_log(payload.action, dialog_room, user.username)
        await dialog_join(sid, payload.data, user.id)
    elif payload.action == LEAVE:
        dialog_room = ROOM_CHANNEL_DIALOG(payload.data)
        format_log(payload.action, dialog_room, user.username)
        sio.leave_room(sid, dialog_room)
    elif payload.action == READ:
        dialog_room = ROOM_CHANNEL_DIALOG(payload.data.get('dialogId'))
        count = await dialog_read(sid, payload.data.get('dialogId'), payload.data.get('messageIds'))
        count and format_log(payload.action, dialog_room, user.username, param_action=count)
    elif payload.action == WRITE:
        dialog_id = payload.data.get('dialogId')
        message_text = payload.data.get('text')
        dialog_room = ROOM_CHANNEL_DIALOG(dialog_id)
        format_log(payload.action, dialog_room, user.username)
        await dialog_write(sid, dialog_id, message_text, user, dialog_room)


@sio.on(CHANNEL_USERS)
async def channel_users(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        result = await get_users_by_dialog_ids(payload.data)
        await sio.emit(CHANNEL_USERS, [dict(item) for item in result], room=sid)


@sio.on('chat')
async def read_message(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == 'init':
        result = await get_user_dialog_statistics(user.id)
        await sio.emit('chat', {
            "action": 'init',
            "data": [dict(item) for item in result]
        }, room=sid)


@sio.on("joinDialog")
async def join_dialog(sid, dialog_id):
    print(f"{sid} enter dialog {dialog_id}")
    sio.enter_room(sid, dialog_id)
