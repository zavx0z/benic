import logging

from chat.actions import JOIN
from chat.channels import CHANNEL_USERS, STATIC_USERS
from shared.socketio.connect import sio

logger = logging.getLogger('action')


def join_user(user):
    """ИНДИВИДУАЛЬНЫЙ
     Подключение к комнате пользователя на канал [users]
     """
    room = STATIC_USERS(user.id)
    sio.enter_room(user.sid, room)
    logger.info(user.id, user.username, user.sid, JOIN, CHANNEL_USERS, room)
