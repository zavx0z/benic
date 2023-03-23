from typing import List

from chat.actions import READ, WRITE
from chat.channerls import ROOM_CHANNEL_DIALOG, CHANNEL_DIALOG
from chat.crud.dialog import get_dialog_by_id, get_messages_count
from chat.crud.message import create_message
from chat.query.insert import set_messages_read
from chat.query.select import get_messages_for_dialog
from chat.schema import SessionUser
from chat.schema.clientresponse import ClientResponse
from chat.schema.message import MessageResponse
from shared import action
from shared.socketio import sio


async def dialog_join(sid: str, dialog_id: int, user_id: int):
    dialog_room = ROOM_CHANNEL_DIALOG(dialog_id)
    messages = await get_messages_for_dialog(dialog_id, user_id)
    sio.enter_room(sid, dialog_room)
    await sio.emit(CHANNEL_DIALOG, {
        "action": action.JOIN,
        "data": {
            "dialogId": dialog_id,
            "messages": [dict(i) for i in messages]
        }
    }, room=dialog_room)


async def dialog_read(sid: str, dialog_id: int, user_id: int, message_ids: List[int]):
    dialog_room = ROOM_CHANNEL_DIALOG(dialog_id)
    reader_ids = await set_messages_read(user_id, message_ids)
    count = len(reader_ids)
    if count:
        await sio.emit(CHANNEL_DIALOG, {
            "action": READ,
            "data": {
                "dialogId": dialog_id,
                "messageIds": message_ids
            }
        }, room=dialog_room)
        return count


async def dialog_write(sid: str, dialog_id: int, message_text: str, user: SessionUser, dialog_room: str):
    dialog = await get_dialog_by_id(dialog_id)
    # рассылка админам при первом сообщении
    if not user.is_superuser:
        count_messages = await get_messages_count(dialog.id)
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog.id)))
    message = await create_message(text=message_text, sender_id=user.id, dialog_id=dialog.id)
    await sio.emit(CHANNEL_DIALOG, {
        'action': WRITE,
        "data": {
            "dialogId": dialog.id,
            "message": dict(MessageResponse(
                id=message.id,
                senderId=message.sender_id,
                created=message.created_at.isoformat(),
                text=message.text,
                read=False))
        }}, room=dialog_room)
