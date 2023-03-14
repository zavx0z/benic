from typing import List

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from chat.schema.message import MessageResponse

router = APIRouter()


@router.get("/api.v1/proxy/{ip}")
async def get_open_proxy(ip: str, authjwt: AuthJWT = Depends()) -> List[MessageResponse]:
    """Открытие прокси для websocket BiB"""
    authjwt.jwt_required()
    return {'success': 'ok'}
