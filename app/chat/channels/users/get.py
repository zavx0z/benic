import logging

from chat.actions import GET
from chat.channels import CHANNEL_USERS, STATIC_USER
from chat.query.users_for_dialogs import get_users_by_dialog_ids
from shared.socketio import sio

logger = logging.getLogger('action')


async def get_for_user_all_contacted_users(user, dialog_ids):
    """Отправляет пользователю данные обо всех участниках диалогов, в которых он участвует"""
    result = await get_users_by_dialog_ids(dialog_ids)
    room = STATIC_USER(user.id)
    await sio.emit(
        event=CHANNEL_USERS,
        room=room,
        data={
            "action": GET,
            "data": [dict(item) for item in result]
        })
    logger.info(user.id, user.username, user.sid, GET, CHANNEL_USERS, room)
