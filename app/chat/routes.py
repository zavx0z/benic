from typing import List

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from chat.crud.dialog import get_dialog_by_user_id_and_name
from chat.crud.message import get_messages_for_dialog
from chat.crud.user import get_users_with_messages_by_owner_dialogs

# from shared.socketio import sio

router = APIRouter()


# @sio.on('join')
# async def handle_join(sid, *args, **kwargs):
#     print(sid)
#     await sio.emit('lobby', 'User joined')


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

# @sio.on('leave')
# async def handle_leave(sid, *args, **kwargs, ):
#     await sio.emit('lobby', 'User left')
class Client(BaseModel):
    id: int
    username: str


@router.get("/api.v1/chat_clients")
async def get_chat_clients(authjwt: AuthJWT = Depends()) -> List[Client]:
    """"""
    authjwt.jwt_required()
    clients = await get_users_with_messages_by_owner_dialogs()
    return [Client(id=client.id, username=client.username) for client in clients]


class Message(BaseModel):
    id: int
    text: str
    senderId: int


@router.get("/api.v1/support/{client_id}")
async def get_chat_clients(client_id: str, authjwt: AuthJWT = Depends()):
    """"""
    authjwt.jwt_required()
    dialog = await get_dialog_by_user_id_and_name(int(client_id), 'support')
    messages = await get_messages_for_dialog(dialog.id)
    return [dict(Message(id=message.id, text=message.text, senderId=message.sender_id)) for message in messages]
