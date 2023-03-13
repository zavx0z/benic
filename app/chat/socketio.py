from urllib.parse import parse_qs

from pydantic import BaseModel

from auth import is_token_valid
from chat.const import DIALOG_NAME, ADMIN_ID, ADMIN_ORIGIN
from chat.crud.dialog import get_dialogs_by_user_id_and_name, create_dialog
from chat.crud.message import create_message
from chat.schema.clientresponse import ClientResponse
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


@sio.on('*')
def catch_all(event, sid, data):
    print(event)


@sio.on('connect')
async def connect(sid, environ, auth):
    # Получить значение ID пользователя из опции query
    query_params = parse_qs(environ['QUERY_STRING'])
    user_id = int(query_params.get('userId', [-1])[0])
    if not user_id: return None
    # Получить значение токена авторизации из заголовка Authorization
    auth_header = environ.get('HTTP_AUTHORIZATION')
    access_token = auth_header.split(' ')[1] if auth_header else None
    if is_token_valid(access_token):
        user = await get_user(user_id)

        print(f"connect {user.username}")
        await sio.save_session(sid, SessionUser(
            id=user.id,
            username=user.username,
            is_superuser=user.is_superuser
        ))

        if user.is_superuser and not any(origin in environ.get("HTTP_ORIGIN") for origin in ADMIN_ORIGIN):
            await sio.emit('error', {"message": "В чате диалоги только для клиентов.", "type": "warning"}, room=sid)
            return

        dialogs = await get_dialogs_by_user_id_and_name(user_id, 'support')
        if not dialogs and not user.is_superuser:
            dialog = await create_dialog(DIALOG_NAME, user.id, [user.id, ADMIN_ID])
            dialogs = [dialog]
        for dialog in dialogs:
            print(f"{user.username} enter dialog {dialog.id}")
            sio.enter_room(sid, dialog.id)
    else:
        await sio.disconnect(sid)
        print(f"not auth {sid}")


@sio.on('disconnect')
async def disconnect(sid, *args, **kwargs):
    user = await sio.get_session(sid)
    if user:
        dialogs = await get_dialogs_by_user_id_and_name(user.id, DIALOG_NAME)
        for dialog in dialogs:
            sio.leave_room(sid, dialog.id)
    print(f"disconnect {sid}")


@sio.on('support')
async def handle_message(sid: str, data: MessageRequest):
    data = MessageRequest(**data)
    user = await sio.get_session(sid)
    dialogs = await get_dialogs_by_user_id_and_name(data.ownerId, DIALOG_NAME)
    dialog = dialogs[0]
    # рассылка админам при первом сообщении
    if not user.is_superuser:
        count_messages = await dialog.get_messages_count()
        if not count_messages:
            await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog.id)))
    message = await create_message(text=data.text, sender_id=user.id, dialog_id=dialog.id)
    print(f"send dialog {dialog.id}")
    await sio.emit('support', dict(MessageResponse(
        id=message.id,
        ownerId=data.ownerId,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text
    )), room=dialog.id)


@sio.on("joinDialog")
async def join_dialog(sid, dialog_id):
    print(f"{sid} enter dialog {dialog_id}")
    sio.enter_room(sid, dialog_id)
