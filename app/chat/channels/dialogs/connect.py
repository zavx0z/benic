import logging

from auth.models import Role
from chat.actions import JOIN
from chat.channels import CHANNEL_DIALOG
from chat.channels.dialogs.join import join_dialog_static_room
from chat.crud.dialog import get_dialogs_by_user_id
from config import ADMIN_ORIGIN
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def check_user_dialog_permissions(user, environ, sid):
    """Проверка прав доступа пользователя к диалогам.
    Если админ зашел из клиентской части
    """
    if user.role.value > Role.developer.value and not any(origin in environ.get("HTTP_ORIGIN") for origin in ADMIN_ORIGIN):
        msg = "В чате диалоги только для клиентов."
        await sio.emit('error', {"message": msg, "type": "warning"}, room=sid)
        logger.warning(user.id, user.username, user.sid, JOIN, CHANNEL_DIALOG, msg)


async def after_connect(sid):
    user = await sio.get_session(sid)
    # Получение списка диалогов пользователя и информации об участниках этих диалогов
    dialogs = await get_dialogs_by_user_id(user.id)
    # ИНФОРМАЦИОННЫЙ подписывает к комнате Диалога где присутствуют User
    for dialog in dialogs:
        join_dialog_static_room(user, dialog.id)
