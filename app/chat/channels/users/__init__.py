import logging

from chat.actions import GET
from chat.channels import CHANNEL_USERS
from chat.channels.users.connect import after_connect
from chat.channels.users.disconnect import after_disconnect
from chat.channels.users.get import get_for_user_all_contacted_users
from chat.schema import ChatPayload
from events import async_event_manager, SIO_CONNECT, SIO_DISCONNECT
from shared.socketio.connect import sio

logger = logging.getLogger('action')

async_event_manager.subscribe(SIO_CONNECT, after_connect)
async_event_manager.subscribe(SIO_DISCONNECT, after_disconnect)


@sio.on(CHANNEL_USERS)
async def channel_users(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        await get_for_user_all_contacted_users(user, payload.data)
