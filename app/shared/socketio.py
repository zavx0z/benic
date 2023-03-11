from random import randint

import socketio
from pydantic import BaseModel

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
    senderId: int
    text: str


class MessageResponse(MessageRequest):
    id: int
    senderName: str


@sio.on('message')
async def handle_message(sid: str, data: MessageRequest):
    data = MessageRequest(**data)
    user = await sio.get_session(sid)
    if not user or user.id != data.senderId:  # если пользователь залогинился под другим пользователем, меняем данные сессии
        user = await get_user(data.senderId)
        await sio.save_session(sid, SessionUser(
            id=user.id,
            username=user.username,
            is_superuser=user.is_superuser
        ))
    response = MessageResponse(
        id=randint(1, 1000),
        senderId=user.id,
        senderName=user.username,
        text=data.text
    )
    await sio.emit('message', dict(response))
