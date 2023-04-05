import logging

from chat.actions import GET, UPDATE, JOIN
from chat.channels import CHANNEL_USERS
from chat.crud.dialog import get_dialogs_by_user_id
from chat.query.users_for_dialogs import get_users_by_dialog_ids
from chat.schema import ChatPayload
from events import SIO_DISCONNECT, async_event_manager, SIO_CONNECT
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def update_user_status_from_dialog_participant(user):
    dialogs = await get_dialogs_by_user_id(user.id)
    dialog_participants = await get_users_by_dialog_ids([item.id for item in dialogs])
    self_participant = next(filter(lambda inst: inst.id == user.id, dialog_participants), None)
    for participant in dialog_participants:
        if participant.id != user.id:
            await sio.emit(
                event=CHANNEL_USERS,
                room=participant.id,
                skip_sid=self_participant.id,
                data={
                    "action": UPDATE,
                    "data": dict(self_participant),
                })
            logger.info(user.id, user.username, user.sid, UPDATE, CHANNEL_USERS, participant.id)


def join(user):
    # ИНДИВИДУАЛЬНЫЙ Подключение к комнате пользователя на канал [users]
    sio.enter_room(user.sid, user.id)
    logger.info(user.id, user.username, user.sid, JOIN, CHANNEL_USERS, user.id)


async def send_for_user_all_contacted_users(user, dialog_ids):
    """Отправляет пользователю данные обо всех участниках диалогов, в которых он участвует"""
    result = await get_users_by_dialog_ids(dialog_ids)
    await sio.emit(
        event=CHANNEL_USERS,
        room=user.id,
        data={
            "action": GET,
            "data": [dict(item) for item in result]
        })
    logger.info(user.id, user.username, user.sid, GET, CHANNEL_USERS, user.id)


async def after_connect(sid):
    user = await sio.get_session(sid)
    join(user)
    dialogs = await get_dialogs_by_user_id(user.id)
    await send_for_user_all_contacted_users(user, [d.id for d in dialogs])
    await update_user_status_from_dialog_participant(user)


async def after_disconnect(sid):
    user = await sio.get_session(sid)
    await update_user_status_from_dialog_participant(user)


async_event_manager.subscribe(SIO_CONNECT, after_connect)
async_event_manager.subscribe(SIO_DISCONNECT, after_disconnect)


@sio.on(CHANNEL_USERS)
async def channel_users(sid: str, payload: ChatPayload):
    user = await sio.get_session(sid)
    payload = ChatPayload(**payload)
    if payload.action == GET:
        await send_for_user_all_contacted_users(user, payload.data)
