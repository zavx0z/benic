import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
sio_app = socketio.ASGIApp(sio)


@sio.on('connect')
async def connect(sid, *args, **kwargs):
    print(f"connect {sid}")


@sio.on('disconnect')
async def disconnect(sid, *args, **kwargs):
    print(f"disconnect {sid}")
