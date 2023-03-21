import socketio

from auth.token import get_jwt_subject
from chat.const import DIALOG_NAME, ADMIN_ORIGIN, ADMIN_ID
from chat.crud.dialog import get_dialogs_by_user_id_and_name, create_dialog
from chat.schema import SessionUser
from shared.crud import get_user

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
sio_app = socketio.ASGIApp(sio)


@sio.on('disconnect')
async def disconnect(sid, *args, **kwargs):
    user = await sio.get_session(sid)
    if user:
        dialogs = await get_dialogs_by_user_id_and_name(user.id, DIALOG_NAME)
        for dialog in dialogs:
            sio.leave_room(sid, dialog.id)
    print(f"disconnect {sid}")


@sio.on('*')
def catch_all(event, sid, data):
    print(event)


@sio.on('connect')
async def connect(sid, environ, auth):
    """
    Проверяет авторизацию клиента и получает токен доступа.
    Идентифицирует пользователя на основе токена доступа.
    Сохраняет информацию о пользователе в сессии.
    Проверяет права доступа пользователя к диалогам.
    Присоединяет пользователя к его диалогам.

    :param auth: словарь с информацией об авторизации клиента (для WebSocket)
    :type auth: dict
    :param environ: словарь с информацией об окружении (для HTTP Polling)
    :type environ: dict
    :param sid: идентификатор клиента
    :type sid: str
    """

    access_token = await get_access_token(sid, auth, environ)
    user = await get_authenticated_user(access_token, sid)
    if user:
        await save_user_to_session(user, sid)
        await check_user_dialog_permissions(user, environ, sid)
        await join_user_dialogs(user, sid)
    else:
        await sio.disconnect(sid)
        print(f"not auth {sid}")


async def get_access_token(sid, auth, environ):
    """Получает токен доступа из авторизации клиента."""
    if auth:
        access_token = auth.get('token')
    elif environ.get('HTTP_AUTHORIZATION'):
        access_token = environ.get('HTTP_AUTHORIZATION').split(' ')[1]
    else:
        await sio.disconnect(sid)
        print(f"not auth {sid}")
    return access_token


async def get_authenticated_user(access_token, sid):
    """Идентифицирует пользователя на основе токена доступа."""
    pk = get_jwt_subject(access_token)
    if pk:
        user = await get_user(pk)
        print(f"connect {user.username}")
        return user
    else:
        await sio.disconnect(sid)
        print(f"not auth {sid}")


async def save_user_to_session(user, sid):
    """Сохраняет информацию о пользователе в сессии."""
    await sio.save_session(sid, SessionUser(
        id=user.id,
        username=user.username,
        is_superuser=user.is_superuser
    ))


async def check_user_dialog_permissions(user, environ, sid):
    """Проверка прав доступа пользователя к диалогам."""
    if user.is_superuser and not any(origin in environ.get("HTTP_ORIGIN") for origin in ADMIN_ORIGIN):
        await sio.emit('error', {"message": "В чате диалоги только для клиентов.", "type": "warning"}, room=sid)


async def join_user_dialogs(user, sid):
    """Присоединяет пользователя к его диалогам.

    - получает все диалоги пользователя, имеющие имя 'support'
    - создается новый диалог, если у пользователя нет диалогов с таким именем и он не является суперпользователем
    - подписывает его к каждому из диалогов
    """
    dialogs = await get_dialogs_by_user_id_and_name(user.id, 'support')
    if not dialogs and not user.is_superuser:
        dialog = await create_dialog(DIALOG_NAME, user.id, [user.id, ADMIN_ID])
        dialogs = [dialog]
    for dialog in dialogs:
        print(f"{user.username} enter dialog {dialog.id}")
        sio.enter_room(sid, dialog.id)
