import logging

from chat.actions import GET
from chat.channels import CHANNEL_CHAT
from chat.channels.users.update import logger
from chat.query.dialogs_statistics import get_user_dialogs_statistics
from chat.schema import ChatPayload
from shared.socketio.connect import sio

logger = logging.getLogger('action')


@sio.on(CHANNEL_CHAT)
async def chat(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        result = await get_user_dialogs_statistics(user.id)

        if user.role.value > 3:  # todo в запросе данных делать проверку на обращение клиента
            result = [item for item in result if item.totalMessages >= 2]

        await sio.emit(CHANNEL_CHAT, {
            "action": GET,
            "data": [dict(item) for item in result]
        }, room=sid)
        logger.info(user.id, user.username, sid, GET, CHANNEL_CHAT, sid)
