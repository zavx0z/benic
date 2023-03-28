import logging

import socketio

from auth.query.devices import get_or_add_user_device, update_device_status
from auth.token import get_jwt_subject
from chat.actions import GET, UPDATE, JOIN
from chat.actions.user_create import create_support_dialog_and_send_welcome_message
from chat.channels import STATIC_DIALOG, CHANNEL_USERS
from chat.crud.dialog import get_dialogs_by_user_id
from chat.query.users_for_dialogs import get_users_by_dialog_ids
from chat.schema import SessionUser
from config import ADMIN_ORIGIN
from events import async_event_manager
from logger import socketio_logger
from shared.crud import get_user
from shared.socketio.header_utils import user_device_from_header_auth, get_access_token

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[], logger=socketio_logger)
sio_app = socketio.ASGIApp(sio)

logger = logging.getLogger('sio')
logger_chat = logging.getLogger('chat')

CONNECT = 'connect'
DISCONNECT = 'disconnect'


async def after_create_user(user_id: int):
    """Инициализация вновь созданного пользователя """
    welcome_text = """Добро пожаловать в наш чат поддержки! 
Если у вас есть вопросы, задавайте их здесь.
Благодарим вас за выбор нашей платформы.
Если у вас есть отзывы или предложения, мы будем рады их услышать. """
    await create_support_dialog_and_send_welcome_message(sio, user_id=user_id, welcome_text=welcome_text)


async_event_manager.subscribe("AFTER_CREATE_USER", after_create_user)


@sio.on(DISCONNECT)
async def disconnect(sid, *args, **kwargs):
    user = await sio.get_session(sid)
    if user:
        await update_device_status(user.id, user.device_id, is_connected=False)
        dialogs = await get_dialogs_by_user_id(user.id)
        user_instances = await get_users_by_dialog_ids([item.id for item in dialogs])
        await notify_users_status_user(user, user_instances)
        for dialog in dialogs:
            sio.leave_room(sid, dialog.id)
        logger.info(DISCONNECT, '', user.username)
    logger.info(DISCONNECT, '', "unanimous")


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

    :param dict auth: словарь с информацией об авторизации клиента (для WebSocket)
    :param dict environ: словарь с информацией об окружении (для HTTP Polling)
    :param str sid: идентификатор клиента
    """
    access_token = get_access_token(sid, auth, environ)
    if access_token:
        logger.info("TOKEN", sid, "✔️")
        user = await get_authenticated_user(access_token, sid)

        if user:
            device_info = user_device_from_header_auth(user.id, auth)
            device = await get_or_add_user_device(user.id, device_info)  # TODO: не надо обновлять статус, когда устройство вновь создано
            device = await update_device_status(user.id, device.id, is_connected=True)

            await sio.save_session(sid, SessionUser(id=user.id, username=user.username, is_superuser=user.is_superuser, device_id=device.id))
            logger.info(device_info.os, user.username, f"SID: {sid}", extra={'action': device_info.model})
            await check_user_dialog_permissions(user, environ, sid)
            await join_room(user, sid)
        else:
            await sio.disconnect(sid)
            logger.error("👽️", '', "не найден")
    else:
        await sio.disconnect(sid)
        logger.info("TOKEN", '', "🖕")


async def get_authenticated_user(access_token, sid):
    """Идентифицирует пользователя на основе токена доступа."""
    pk = get_jwt_subject(access_token)
    if pk:
        user = await get_user(pk)
        return user
    else:
        await sio.disconnect(sid)


async def check_user_dialog_permissions(user, environ, sid):
    """Проверка прав доступа пользователя к диалогам.
    Если админ зашел из клиентской части
    """
    if user.is_superuser and not any(origin in environ.get("HTTP_ORIGIN") for origin in ADMIN_ORIGIN):
        await sio.emit('error', {"message": "В чате диалоги только для клиентов.", "type": "warning"}, room=sid)
        logger_chat("Админ! ты что тут забыл?")


async def notify_users_status_user(user, user_instances):
    """ Отправляет всем пользователям в диалогах данные о себе,
     который только что присоединился к комнате.

    :param user: объект User, который только что присоединился к комнате
    :param user_instances: список объектов User, которые находятся в тех же диалогах, что и user
    :return: None
    """
    self_instance = next(filter(lambda inst: inst.id == user.id, user_instances), None)
    for instance in user_instances:
        await sio.emit(CHANNEL_USERS, {
            "action": UPDATE,
            "data": dict(self_instance)
        }, room=instance.id)


async def join_room(user: SessionUser, sid: str) -> None:
    """
    Присоединяет пользователя к его комнате на канале [users] и информационно подписывает его на комнаты диалогов,
    в которых он участвует. Также отправляет ему данные о себе и всем остальным пользователям, участвующим в этих
    диалогах.

    :param user: экземпляр класса User, представляющий пользователя, который присоединяется к комнате
    :param sid: уникальный идентификатор сокет-соединения пользователя
    """

    # ИНДИВИДУАЛЬНЫЙ Подключение к комнате пользователя на канал [users]
    sio.enter_room(sid, user.id)
    # logger.info(JOIN, f"{user.username} ROOM: {user.id}")
    # Получение списка диалогов пользователя и информации об участниках этих диалогов
    dialogs = await get_dialogs_by_user_id(user.id)
    user_instances = await get_users_by_dialog_ids([d.id for d in dialogs])

    # Отправляет пользователю данные обо всех участниках диалогов, в которых он участвует
    await sio.emit(CHANNEL_USERS, {
        "action": GET,
        "data": [dict(item) for item in user_instances if item.id != user.id]
    }, room=user.id)

    # ИНФОРМАЦИОННЫЙ подписывает к комнате Диалога где присутствуют User
    for dialog in dialogs:
        sio.enter_room(sid, STATIC_DIALOG(dialog.id))

    await notify_users_status_user(user, user_instances)
