from typing import Optional

import socketio
from pydantic import BaseModel

from chat.crud.dialog import create_dialog, get_dialog_by_user_id_and_name
from chat.crud.message import create_message
from shared.crud import get_user

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
sio_app = socketio.ASGIApp(sio)


@sio.on('connect')
async def connect(sid, *args, **kwargs):
    print(f"connect {sid}")


@sio.on('disconnect')
async def disconnect(sid, *args, **kwargs):
    print(f"disconnect {sid}")


class SessionUser(BaseModel):
    id: int
    username: str
    is_superuser: bool


class MessageRequest(BaseModel):
    ownerDialog: Optional[int]
    senderId: int
    text: str


class MessageResponse(MessageRequest):
    id: int
    senderName: str


ADMIN_ID = 1
DIALOG_NAME = 'support'


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
    owner_dialog = None
    if not user.is_superuser:
        dialog_name = f"support"
        dialog = await get_dialog_by_user_id_and_name(user.id, dialog_name)
        if not dialog:
            dialog = await create_dialog(dialog_name, user.id, [user.id, ADMIN_ID])
        owner_dialog = dialog.owner_id
    else:
        owner_dialog = data.ownerDialog

    # Сообщение
    message = await create_message(text=data.text, sender_id=user.id, dialog_id=dialog.id)
    response = MessageResponse(
        id=message.id,
        ownerDialog=owner_dialog,
        senderId=message.sender_id,
        senderName=user.username,
        text=message.text
    )
    await sio.emit('message', dict(response))
