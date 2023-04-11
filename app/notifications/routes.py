from fastapi import APIRouter, Depends
from fastapi_another_jwt_auth import AuthJWT

from clients.utils import device_from_client
from notifications.tasks import notification_subscribe

router = APIRouter()


@router.post("/api.v1/notification/subscribe")
async def subscribe(payload: dict, authjwt: AuthJWT = Depends()):
    authjwt.jwt_required()
    pk = authjwt.get_jwt_subject()
    token = payload.get('token')
    notification_subscribe.send_with_options(args=(pk, payload.get('device'), token))
