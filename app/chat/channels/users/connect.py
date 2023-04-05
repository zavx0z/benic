import logging

from chat.actions import JOIN
from chat.channels import CHANNEL_USERS
from chat.channels.users.get import get_for_user_all_contacted_users
from chat.channels.users.update import update_user_status_from_dialog_participant
from chat.crud.dialog import get_dialogs_by_user_id
from shared.socketio.connect import sio

logger = logging.getLogger('action')


def join(user):
    # ИНДИВИДУАЛЬНЫЙ Подключение к комнате пользователя на канал [users]
    sio.enter_room(user.sid, user.id)
    logger.info(user.id, user.username, user.sid, JOIN, CHANNEL_USERS, user.id)


async def after_connect(sid):
    user = await sio.get_session(sid)
    join(user)
    dialogs = await get_dialogs_by_user_id(user.id)
    await get_for_user_all_contacted_users(user, [d.id for d in dialogs])
    await update_user_status_from_dialog_participant(user)
