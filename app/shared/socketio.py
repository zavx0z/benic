import logging

import socketio

from auth.query.devices import add_user_device, update_device_status
from auth.schema.device import DeviceBase
from auth.token import get_jwt_subject
from chat.actions import JOIN, UPDATE
from chat.channels import CHANNEL_SUPPORT, STATIC_DIALOG, CHANNEL_DIALOG, DYNAMIC_DIALOG, CHANNEL_USERS
from chat.crud.dialog import get_dialogs_by_user_id_and_name, create_dialog
from chat.crud.message import create_message
from chat.query.dialogs_statistics import get_user_dialog_statistics
from chat.query.select import get_users_by_dialog_ids
from chat.schema import SessionUser
from chat.schema.message import MessageResponse, MessageInfo
from config import ADMIN_ID, ADMIN_ORIGIN
from shared import action
from shared.crud import get_user

# Настраиваем логгер Socket.IO
socketio_logger = logging.getLogger('socketio')
socketio_logger.setLevel(logging.DEBUG)
# Создаем обработчик логов для вывода сообщений в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
socketio_logger.addHandler(console_handler)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[], logger=socketio_logger)
sio_app = socketio.ASGIApp(sio)

logger = logging.getLogger('sio')

CONNECT = 'connect'
DISCONNECT = 'disconnect'


@sio.on(DISCONNECT)
async def disconnect(sid, *args, **kwargs):
    user = await sio.get_session(sid)
    if user:
        await update_device_status(user.device_id, is_connected=False)
        dialogs = await get_dialogs_by_user_id_and_name(user.id, CHANNEL_SUPPORT)
        for dialog in dialogs:
            sio.leave_room(sid, dialog.id)
    logger.info(DISCONNECT, '', user.username)


@sio.on('*')
def catch_all(event, sid, data):
    print(event)


@sio.on(CONNECT)
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
        device = auth.get('device')
        device_inst = await add_user_device(user.id, DeviceBase(
            user_agent=device.get('userAgent', device.get('ua')),
            is_mobile=device.get('isMobile', False),
            vendor=device.get('vendor'),
            model=device.get('model'),
            os=device.get('osName', device.get('os')),
            os_version=device.get('osVersion'),
        ))
        logger.info(CONNECT, '', user.username)
        await sio.save_session(sid, SessionUser(id=user.id, username=user.username, is_superuser=user.is_superuser, device_id=device_inst.id))
        await check_user_dialog_permissions(user, environ, sid)
        await join_user_dialogs(user, sid)
    else:
        await sio.disconnect(sid)
        logger.info(DISCONNECT, 'not auth', user.username)


async def get_access_token(sid, auth, environ):
    """Получает токен доступа из авторизации клиента."""
    if auth:
        access_token = auth.get('token')
    elif environ.get('HTTP_AUTHORIZATION'):
        access_token = environ.get('HTTP_AUTHORIZATION').split(' ')[1]
    else:
        await sio.disconnect(sid)
    return access_token


async def get_authenticated_user(access_token, sid):
    """Идентифицирует пользователя на основе токена доступа."""
    pk = get_jwt_subject(access_token)
    if pk:
        user = await get_user(pk)
        return user
    else:
        await sio.disconnect(sid)


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
    if not dialogs and not user.is_superuser:  # todo manager
        dialog = await create_dialog(CHANNEL_SUPPORT, user.id, [user.id, ADMIN_ID])
        text = '''
Добро пожаловать в наш чат поддержки!

Если у вас есть какие-либо вопросы, пиши сюда.

Спасибо, что выбрали нашу платформу, и мы надеемся...! Если у вас есть какие-либо отзывы или предложения, мы будем рады услышать их.
                '''
        dialogs = [dialog]
        for dialog in dialogs:
            logger.info(JOIN, STATIC_DIALOG(dialog.id), user.username)
            sio.enter_room(sid, STATIC_DIALOG(dialog.id))
        result = await get_users_by_dialog_ids([dialog.id])
        await sio.emit(CHANNEL_USERS, [dict(item) for item in result], room=sid)

        message = await create_message(
            text=text,
            dialog_id=dialog.id,
            sender_id=1
        )

        result = await get_user_dialog_statistics(user.id)
        if dialog.name == 'support':
            DYNAMIC = DYNAMIC_DIALOG(dialog.id)
            sio.enter_room(sid, DYNAMIC)

            await sio.emit('chat', {
                "action": 'init',
                "data": [dict(item) for item in result]
            }, room=sid)

            await sio.emit(CHANNEL_DIALOG, {
                'action': action.WRITE,
                "data": {
                    "dialogId": dialog.id,
                    "message": dict(MessageResponse(
                        id=message.id,
                        senderId=message.sender_id,
                        created=message.created_at.isoformat(),
                        text=message.text,
                        read=False))

                }}, room=DYNAMIC_DIALOG(dialog.id))
            await sio.emit(CHANNEL_DIALOG, {
                'action': UPDATE,
                "data": {
                    "dialogId": dialog.id,
                    "message": dict(MessageInfo(
                        lastMessageSenderId=message.sender_id,
                        lastMessageTime=message.created_at.isoformat(),
                        lastMessageText=message.text[:min(len(message.text), 40)]
                    ))
                }}, room=STATIC_DIALOG(dialog.id))

            logger.info(UPDATE, STATIC_DIALOG(dialog.id), user.username)
