from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from client.query import get_or_add_user_device, update_device_notification_token
from client.utils import device_from_client
from notifications.utils import send_notification_to_user

router = APIRouter()


@router.post("/api.v1/notification/subscribe")
async def subscribe(payload: dict, authjwt: AuthJWT = Depends()):
    authjwt.jwt_required()
    pk = authjwt.get_jwt_subject()
    token = payload.get('token')
    device_client = device_from_client(payload.get('device'))
    device_db = await get_or_add_user_device(pk, device_client)
    if token != device_db.notification_token:
        device = await update_device_notification_token(device_db.id, token)
        send_notification_to_user(device.notification_token, 'Botswork', 'Вы подписаны на оповещения.')
        return {"subscribed": 'OK'}
    return {"subscribe": 'exist'}
