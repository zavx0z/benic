import logging

from chat.actions import GET
from chat.channels import CHANNEL_USERS
from users.actions.connect import after_connect
from users.actions.disconnect import after_disconnect
from users.actions.get import get_for_user_all_contacted_users
from chat.schema import ChatPayload
from events import async_event_manager, SIO_CONNECT, SIO_DISCONNECT
from shared.socketio import sio

logger = logging.getLogger('action')

async_event_manager.subscribe(SIO_CONNECT, after_connect)
async_event_manager.subscribe(SIO_DISCONNECT, after_disconnect)


@sio.on(CHANNEL_USERS)
async def channel_users(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        await get_for_user_all_contacted_users(user, payload.data)
