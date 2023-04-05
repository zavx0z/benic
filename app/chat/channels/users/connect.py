import logging

from chat.channels.users.get import get_for_user_all_contacted_users
from chat.channels.users.join import join_user
from chat.channels.users.update import update_user_status_from_dialog_participant
from chat.crud.dialog import get_dialogs_by_user_id
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def after_connect(sid):
    user = await sio.get_session(sid)
    join_user(user)
    dialogs = await get_dialogs_by_user_id(user.id)
    await get_for_user_all_contacted_users(user, [d.id for d in dialogs])
    await update_user_status_from_dialog_participant(user)
