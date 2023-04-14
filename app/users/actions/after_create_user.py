import logging

from chat.actions import PUT
from chat.channels import STATIC_USER, CHANNEL_USERS
from config import ADMIN_ID
from shared.socketio import sio
from users.query.users_for_admin import get_user_for_admin

logger = logging.getLogger('action')


async def after_create_user(user_id: int):
    user = await get_user_for_admin(user_id)
    room = STATIC_USER(ADMIN_ID)
    await sio.emit(
        event=CHANNEL_USERS,
        room=room,
        data={
            "action": PUT,
            "data": dict(user)
        })
    logger.info(user.id, 'user.username', 'user.sid', PUT, CHANNEL_USERS, room)
