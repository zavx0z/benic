from chat.channels import STATIC_USER
from shared.socketio import sio


@sio.on('remoteLog')
async def remoteLog(sid, payload):
    user = await sio.get_session(sid)
    await sio.emit('userLog', payload, STATIC_USER(1))
