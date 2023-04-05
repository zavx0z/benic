from chat.channels.users.update import update_user_status_from_dialog_participant
from shared.socketio.connect import sio


async def after_disconnect(sid):
    user = await sio.get_session(sid)
    await update_user_status_from_dialog_participant(user)