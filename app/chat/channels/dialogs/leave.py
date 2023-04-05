import logging
from typing import List

from chat.actions import LEAVE
from chat.channels import DYNAMIC_DIALOG, CHANNEL_DIALOG, STATIC_DIALOG
from shared.socketio.connect import sio

logger = logging.getLogger('action')


def leave_dialog_dynamic_room(user, dialog_id):
    room = DYNAMIC_DIALOG(dialog_id)
    sio.leave_room(user.sid, room)
    logger.info(user.id, user.username, user.sid, LEAVE, CHANNEL_DIALOG, room)


async def leave_dialog_static_room(sid: str, user, dialog_ids: List[int]):
    for idx in dialog_ids:
        STATIC = STATIC_DIALOG(idx)
        sio.leave_room(sid, idx)
        logger.info(user.id, user.username, sid, LEAVE, STATIC_DIALOG, STATIC)
