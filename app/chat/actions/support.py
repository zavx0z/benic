import logging

from sso.crud.user import get_user
from chat.actions import UPDATE
from chat.channels import STATIC_USER, CHANNEL_CHAT
from users.query.users_for_client import get_users_by_dialog_ids
from config import ADMIN_ID
from shared.socketio import sio

logger = logging.getLogger('action')


async def emit_admin_update_chat(user_id, dialog_id: int, msg):
    admin = await get_user(ADMIN_ID)
    room = STATIC_USER(admin.id)
    users = await get_users_by_dialog_ids([dialog_id])
    await sio.emit(
        event=CHANNEL_CHAT,
        room=room,
        data={
            "action": UPDATE,
            "data": {
                "dialog": {
                    'id': dialog_id,
                    'name': 'support',
                    'ownerId': user_id,
                    'totalMessages': 2,
                    'unreadMessages': 1,
                    'lastMessageText': msg.text,
                    'lastMessageTime': msg.created_at.isoformat(),
                    'lastMessageSenderId': user_id,
                    'participants': [user_id, ADMIN_ID]
                },
                "users": [dict(user) for user in users if user.id != ADMIN_ID]
            }
        })
    logger.info(admin.id, admin.username, '', UPDATE, CHANNEL_CHAT, room)
