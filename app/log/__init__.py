from chat.channels import STATIC_USER
from shared.socketio import sio


@sio.on('remoteLog')
async def remoteLog(sid, payload):
    user = await sio.get_session(sid)
    print(payload)
    await sio.emit('userLog', {"userId": user.id, "log": payload}, STATIC_USER(1))
