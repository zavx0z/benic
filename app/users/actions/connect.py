import logging

from chat.crud.dialog import get_participant_dialogs
from shared.socketio import sio
from users.actions.get import get_for_user_all_contacted_users, emit_users_fof_admin
from users.actions.join import join_user
from users.actions.update import update_user_status_from_dialog_participant

logger = logging.getLogger('action')


async def after_connect(sid):
    user = await sio.get_session(sid)
    join_user(user)

    dialogs = await get_participant_dialogs(user.id)
    if user.role.value >= 10:
        await emit_users_fof_admin(user)
    else:
        await get_for_user_all_contacted_users(user, [d.id for d in dialogs])
    await update_user_status_from_dialog_participant(user)  # todo передавать id диалогов
