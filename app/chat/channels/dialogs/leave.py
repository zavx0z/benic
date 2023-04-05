import logging

from chat.actions import LEAVE
from chat.channels import DYNAMIC_DIALOG, CHANNEL_DIALOG
from shared.socketio.connect import sio

logger = logging.getLogger('action')


def leave_dialog_dynamic(user, dialog_id):
    room = DYNAMIC_DIALOG(dialog_id)
    sio.leave_room(user.sid, room)
    logger.info(user.id, user.username, user.sid, LEAVE, CHANNEL_DIALOG, room)
