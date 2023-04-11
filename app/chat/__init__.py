import logging
from chat.actions import GET
from chat.channels import CHANNEL_CHAT
from chat.query.dialogs_statistics import get_user_dialogs_statistics
from chat.schema import ChatPayload
from shared.socketio import sio

logger = logging.getLogger('action')


@sio.on(CHANNEL_CHAT)
async def chat(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    # payload = ChatPayload(**payload)
    result = await get_user_dialogs_statistics(user.id)
    if user.role.value > 3:
        result = [item for item in result if item.totalMessages >= 2]
    logger.info(user.id, user.username, sid, GET, CHANNEL_CHAT, sid)
    return [dict(item) for item in result]
