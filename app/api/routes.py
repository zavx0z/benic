from app import socketio
from flask_socketio import emit


@socketio.on('my event')
def handle_my_custom_event(json):
    print('message')
    emit('my response', json)


@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
