from chat.actions import GET
from chat.channels import CHANNEL_USERS
from chat.query.select import get_users_by_dialog_ids
from chat.schema import ChatPayload
from shared.socketio import sio


@sio.on(CHANNEL_USERS)
async def channel_users(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        result = await get_users_by_dialog_ids(payload.data)
        await sio.emit(CHANNEL_USERS, {
            "action": GET,
            "data": [dict(item) for item in result]
        }, room=user.id)
