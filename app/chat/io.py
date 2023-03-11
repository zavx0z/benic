from random import randint

from shared.crud import get_user
from shared.socketio import sio


@sio.on('join')
async def handle_join(sid, *args, **kwargs):
    print(sid)
    await sio.emit('lobby', 'User joined')


# @sio.on('message')
# async def handle_message(sid, data):
#     session = await sio.get_session(sid)
#     user_id = data.get('sender')
#     if not session:
#         user = await get_user(user_id)
#         data['senderName'] = user.username
#         await sio.save_session(sid, {'id': user.id, 'username': user.username})
#     else:
#         data['senderName'] = session.get('username')
#     data.update({"id": randint(1, 1000)})
#     await sio.emit('message', data)
#

@sio.on('leave')
async def handle_leave(sid, *args, **kwargs, ):
    await sio.emit('lobby', 'User left')
