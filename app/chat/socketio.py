from pydantic import BaseModel

from chat.const import DIALOG_NAME
from chat.crud.dialog import get_dialog_by_user_id_and_name
from chat.crud.message import create_message
from chat.schema.message import MessageResponse
from shared.crud import get_user
from shared.socketio import sio


class SessionUser(BaseModel):
    id: int
    username: str
    is_superuser: bool


class MessageRequest(BaseModel):
    ownerId: int
    senderId: int
    text: str


@sio.on('joinSupport')
async def join_support(sid: str):
    pass


@sio.on('support')
async def handle_message(sid: str, data: MessageRequest):
    data = MessageRequest(**data)
    # Пользователь
    user = await sio.get_session(sid)
    if not user or user.id != data.senderId:  # если пользователь залогинился под другим пользователем, меняем данные сессии
        user = await get_user(data.senderId)
        await sio.save_session(sid, SessionUser(
            id=user.id,
            username=user.username,
            is_superuser=user.is_superuser
        ))
    # Диалог пользователя
    dialog = await get_dialog_by_user_id_and_name(data.ownerId, DIALOG_NAME)

    # Сообщение
    message = await create_message(text=data.text, sender_id=user.id, dialog_id=dialog.id)
    await sio.emit('support', dict(MessageResponse(
        id=message.id,
        ownerId=data.ownerId,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text
    )))
