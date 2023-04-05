import logging

from chat.actions import GET
from chat.channels import CHANNEL_CHAT
from chat.crud.dialog import get_messages_count
from chat.query.dialogs_statistics import get_user_dialog_statistics
from chat.schema import ChatPayload
from chat.schema.clientresponse import ClientResponse
from shared.socketio.connect import sio

logger = logging.getLogger('action')


# async_event_manager.subscribe('dialog_created', my_function)
async def send_admin_is_first_message_support_dialog(user, dialog_id):
    if not user.is_superuser:  # рассылка админам при первом сообщении todo
        count_messages = await get_messages_count(dialog_id)
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog_id)))


@sio.on('chat')
async def read_message(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        result = await get_user_dialog_statistics(user.id)
        await sio.emit(CHANNEL_CHAT, {
            "action": GET,
            "data": [dict(item) for item in result]
        }, room=sid)
        logger.info(user.id, user.username, sid, GET, CHANNEL_CHAT, sid)
