from typing import List

from shared.session import SessionUser
from shared.socketio import sio


async def get_users_session_for_room(room: str) -> List[SessionUser]:
    users = [await sio.get_session(i[0]) for i in sio.manager.get_participants('/', room)]
    return users
