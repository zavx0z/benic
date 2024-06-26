import logging

from chat.actions import UPDATE
from chat.channels import CHANNEL_USERS, STATIC_USER
from chat.crud.dialog import get_participant_dialogs
from users.query.users_for_client import get_users_by_dialog_ids
from shared.socketio import sio

logger = logging.getLogger('action')


async def update_user_status_from_dialog_participant(user):
    dialogs = await get_participant_dialogs(user.id)
    dialog_participants = await get_users_by_dialog_ids([item.id for item in dialogs])
    self_participant = next(filter(lambda inst: inst.id == user.id, dialog_participants), None)
    for participant in dialog_participants:
        if participant.id != user.id:
            room = STATIC_USER(participant.id)
            await sio.emit(
                event=CHANNEL_USERS,
                room=room,
                skip_sid=self_participant.id,
                data={
                    "action": UPDATE,
                    "data": dict(self_participant),
                })
            logger.info(user.id, user.username, user.sid, UPDATE, CHANNEL_USERS, room)


