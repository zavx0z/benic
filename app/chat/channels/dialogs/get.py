import logging

from chat.actions import GET
from chat.channels import DYNAMIC_DIALOG, CHANNEL_DIALOG
from chat.query.select import get_messages_for_dialog
from shared.socketio import sio

logger = logging.getLogger('action')


async def get_dialog(user, dialog_id):
    messages = await get_messages_for_dialog(dialog_id, user.id)
    room = DYNAMIC_DIALOG(dialog_id)
    await sio.emit(
        event=CHANNEL_DIALOG,
        room=room,
        data={
            "action": GET,
            "data": {
                "dialogId": dialog_id,
                "messages": [dict(i) for i in messages]
            }
        })
    logger.info(user.id, user.username, user.sid, GET, CHANNEL_DIALOG, room)
