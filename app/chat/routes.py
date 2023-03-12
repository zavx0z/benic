from typing import List

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from chat.const import DIALOG_NAME, ADMIN_ID
from chat.crud.dialog import get_dialog_by_user_id_and_name, create_dialog
from chat.crud.message import get_messages_for_dialog
from chat.crud.user import get_users_with_messages_by_owner_dialogs
from chat.schema.message import MessageResponse
from shared.crud import get_user

router = APIRouter()


class Client(BaseModel):
    id: int
    username: str


@router.get("/api.v1/chat/clients")
async def get_chat_clients(authjwt: AuthJWT = Depends()) -> List[Client]:
    """"""
    authjwt.jwt_required()
    clients = await get_users_with_messages_by_owner_dialogs()
    return [Client(id=client.id, username=client.username) for client in clients]


@router.get("/api.v1/chat/support/{client_id}")
async def get_chat_clients(client_id: str, authjwt: AuthJWT = Depends()) -> List[MessageResponse]:
    """"""
    authjwt.jwt_required()
    dialog = await get_dialog_by_user_id_and_name(int(client_id), 'support')
    if not dialog:
        user = await get_user(int(client_id))
        if not user.is_superuser:
            dialog = await create_dialog(DIALOG_NAME, user.id, [user.id, ADMIN_ID])
    messages = await get_messages_for_dialog(dialog.id)
    return [MessageResponse(
        id=message.id,
        ownerId=dialog.owner_id,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text,
    ) for message in messages]
