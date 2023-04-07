import logging

from chat.actions import JOIN
from chat.channels import DYNAMIC_DIALOG, CHANNEL_DIALOG, STATIC_DIALOG
from shared.socketio.connect import sio

logger = logging.getLogger('action')


def join_dialog_dynamic_room(user, dialog_id):
    room = DYNAMIC_DIALOG(dialog_id)
    sio.enter_room(user.sid, room)
    logger.info(user.id, user.username, user.sid, JOIN, CHANNEL_DIALOG, room)


def join_dialog_static_room(user, dialog_id):
    room = STATIC_DIALOG(dialog_id)
    sio.enter_room(user.sid, room)
    logger.info(user.id, user.username, user.sid, JOIN, CHANNEL_DIALOG, room)
