import logging

from chat.actions import GET
from chat.channels import CHANNEL_USERS
from chat.schema import ChatPayload
from events import async_event_manager, SIO_CONNECT, SIO_DISCONNECT, DB_CREATE_USER
from shared.socketio import sio
from .actions.connect import after_connect
from .actions.after_create_user import after_create_user
from .actions.disconnect import after_disconnect
from .actions.get import get_for_user_all_contacted_users, emit_users_fof_admin
from .query.users_for_admin import get_user_for_admin

logger = logging.getLogger('action')

async_event_manager.subscribe(SIO_CONNECT, after_connect)
async_event_manager.subscribe(SIO_DISCONNECT, after_disconnect)
async_event_manager.subscribe(DB_CREATE_USER, after_create_user)


@sio.on(CHANNEL_USERS)
async def channel_users(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    if user.role.value >= 10:
        await emit_users_fof_admin(user)
    else:
        payload = ChatPayload(**payload)
        if payload.action == GET:
            await get_for_user_all_contacted_users(user, payload.data)
