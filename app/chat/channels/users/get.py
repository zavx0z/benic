import logging

from chat.actions import GET
from chat.channels import CHANNEL_USERS
from chat.query.users_for_dialogs import get_users_by_dialog_ids
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def get_for_user_all_contacted_users(user, dialog_ids):
    """Отправляет пользователю данные обо всех участниках диалогов, в которых он участвует"""
    result = await get_users_by_dialog_ids(dialog_ids)
    await sio.emit(
        event=CHANNEL_USERS,
        room=user.id,
        data={
            "action": GET,
            "data": [dict(item) for item in result]
        })
    logger.info(user.id, user.username, user.sid, GET, CHANNEL_USERS, user.id)
