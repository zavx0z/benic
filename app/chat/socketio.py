from chat.actions import GET, JOIN, LEAVE, READ, WRITE
from chat.actions.dialog import dialog_join, dialog_read, dialog_write
from chat.channerls import ROOM_CHANNEL_DIALOG, CHANNEL_DIALOG, CHANNEL_USERS
from chat.query.dialogs_statistics import get_user_dialog_statistics
from chat.query.select import get_users_by_dialog_ids
from chat.schema import ChatPayload
from shared.socketio import sio

format_log = lambda action, room, username, param_action=None: print(f"{action.upper():7}{'' if param_action is None else param_action} {room:10} from: {username}")


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
        count = await dialog_read(
            sid=sid,
            user_id=user.id,
            dialog_id=payload.data.get('dialogId'),
            message_ids=payload.data.get('messageIds')
        )
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

# await sio.emit('support', message, room=dialog.id)
# await sio.emit('message', {"dialogId": dialog.id, "message": message}, room=ROOM_CHANNEL_DIALOG(dialog.id))
# await sio.emit(CHANNEL_DIALOG, {"dialogId": dialog.id, "unreadMessages": 1}, room=ROOM_CHANNEL_DIALOG(dialog.id), skip_sid=sid)
