import logging

import socketio

from clients.query.async_query import get_or_add_user_device, update_device_status
from clients.schema import DevicePayloadSchema
from config import ASYNC_REDIS_MANAGER
from events import async_event_manager, SIO_DISCONNECT, SIO_CONNECT
from logger import socketio_logger
from shared.session import SessionUser
from sso.crud.user import get_user
from sso.socketio import get_access_token
from sso.token import get_jwt_subject

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],
    logger=socketio_logger,
    client_manager=socketio.AsyncRedisManager(ASYNC_REDIS_MANAGER)
)

sio_app = socketio.ASGIApp(sio)

logger = logging.getLogger('action')

CONNECT = 'connect'
DISCONNECT = 'disconnect'


@sio.on('*')
def catch_all(event, sid, data):
    print(event)


@sio.on(CONNECT)
async def connect(sid, environ, auth):
    """ Подключение соединения.
    - Проверяет авторизацию клиента и получает токен доступа.
    - Идентифицирует пользователя на основе токена доступа.
    - Сохраняет информацию о пользователе в сессии.
    - Вызывает функции подписанные на событие SIO_CONNECT

    :param str sid: идентификатор клиента
    :param dict environ: словарь с информацией об окружении (для HTTP Polling)
    :param dict auth: словарь с информацией об авторизации клиента (для WebSocket)
    """
    ip = environ['REMOTE_ADDR']
    access_token = get_access_token(sid, auth, environ)
    pk = get_jwt_subject(access_token)
    if pk:
        user = await get_user(pk)
        device_info = DevicePayloadSchema(**auth.get('device'))
        device = await get_or_add_user_device(user.id, device_info, ip)  # TODO: не надо обновлять статус, когда устройство вновь создано
        device = await update_device_status(user.id, device.id, is_connected=True)
        await sio.save_session(sid, SessionUser(
            sid=sid,
            id=user.id,
            username=user.username,
            role=user.role,
            device_id=device.id
        ))
        logger.info(user.id, user.username, sid, CONNECT, device_info.os, device_info.model)
        await async_event_manager.notify(SIO_CONNECT, sid)  # Событие менеджеру
        await sio.emit('remoteLog', True, room=sid)
    else:
        await sio.disconnect(sid)
        logger.error('-', 'anon', sid, CONNECT, "token", "не найден")


@sio.on(DISCONNECT)
async def disconnect(sid, *args, **kwargs):
    """ Отключает соединение.
        - Обновляет статус девайса пользователя
        - Вызывает функции подписанные на событие SIO_CONNECT
    """
    user = await sio.get_session(sid)
    if user:
        await update_device_status(user.id, user.device_id, is_connected=False)
        await async_event_manager.notify(SIO_DISCONNECT, sid)  # Событие менеджеру
        logger.info(user.id, user.username, user.sid, DISCONNECT, 'device', user.device_id)
    else:
        logger.error('-', 'anon', sid, DISCONNECT, "", "")
