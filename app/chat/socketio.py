import logging

from chat.crud.dialog import get_messages_count
from chat.query.dialogs_statistics import get_user_dialog_statistics
from chat.schema import ChatPayload
from chat.schema.clientresponse import ClientResponse
from shared.socketio.connect import sio

logger = logging.getLogger('sio')
logger_chat = logging.getLogger('chat')


# async_event_manager.subscribe('dialog_created', my_function)
async def send_admin_is_first_message_support_dialog(user, dialog_id):
    if not user.is_superuser:  # рассылка админам при первом сообщении todo
        count_messages = await get_messages_count(dialog_id)
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog_id)))


@sio.on('chat')
async def read_message(sid: str, payload: ChatPayload):
    logger_chat.debug(payload)
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
