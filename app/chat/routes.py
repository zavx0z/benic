from typing import List

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from chat.crud.dialog import get_dialogs_by_user_id_and_name
from chat.crud.message import get_messages_for_dialog
from chat.crud.user import get_users_with_messages_by_owner_dialogs
from chat.schema.clientresponse import ClientResponse
from chat.schema.message import MessageResponse

router = APIRouter()


@router.get("/api.v1/chat/clients")
async def get_chat_clients(authjwt: AuthJWT = Depends()) -> List[ClientResponse]:
    """"""
    authjwt.jwt_required()
    clients = await get_users_with_messages_by_owner_dialogs()
    return [ClientResponse(id=client.id, username=client.username) for client in clients]


@router.get("/api.v1/chat/support/{client_id}")  # fixme нет истории у суперпользователя
async def get_messages_for_client(client_id: str, authjwt: AuthJWT = Depends()) -> List[MessageResponse]:
    """"""
    authjwt.jwt_required()
    dialogs = await get_dialogs_by_user_id_and_name(int(client_id), 'support')
    dialog = dialogs[0]
    messages = await get_messages_for_dialog(dialog.id)
    return [MessageResponse(
        id=message.id,
        ownerId=dialog.owner_id,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text,
    ) for message in messages]
