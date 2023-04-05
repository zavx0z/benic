import logging

from chat.actions import READ
from chat.channels import CHANNEL_DIALOG, DYNAMIC_DIALOG
from chat.query.insert import set_messages_read
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def read(user, dialog_id, message_ids):
    room = DYNAMIC_DIALOG(dialog_id)
    reader_ids = await set_messages_read(user.id, message_ids)
    if len(reader_ids):
        await sio.emit(
            event=CHANNEL_DIALOG,
            room=room,
            data={
                "action": READ,
                "data": {
                    "dialogId": dialog_id,
                    "messageIds": message_ids
                }}
        )
        logger.info(user.id, user.username, user.sid, READ, CHANNEL_DIALOG, room)
