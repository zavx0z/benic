import logging
from enum import Enum

from dramatiq_abort import abort
from dramatiq_abort.middleware import AbortMode
from fastapi import APIRouter, Depends
from fastapi_another_jwt_auth import AuthJWT
from pydantic import BaseModel

from chat.channels import STATIC_USER
from log.tasks import tail_logs
from shared.socketio import sio
from shared.utils.sio import get_users_session_for_room
from sso.crud.user import get_user
from worker import get_running_tasks

router = APIRouter()
logger = logging.getLogger('action')


@router.post("/api.v1/log/start")
async def start_tail_logs(authjwt: AuthJWT = Depends()):
    authjwt.jwt_required()
    pk = authjwt.get_jwt_subject()
    user = await get_user(pk)

    tasks = get_running_tasks()
    if not len([task for task in tasks if task.actor_name == 'tail_logs']):
        tail_logs.send('app.log')
        logger.info(user.id, user.username, 'sid', 'START', 'log', 'broadcast')


@router.post("/api.v1/log/stop")
async def stop_tail_logs(authjwt: AuthJWT = Depends()):
    authjwt.jwt_required()
    pk = authjwt.get_jwt_subject()
    user = await get_user(pk)

    tasks = get_running_tasks()
    task = next(filter(lambda v: v.actor_name == 'tail_logs', tasks), None)
    if task:
        abort(message_id=task.message_id, mode=AbortMode.ABORT, abort_timeout=1000)
        logger.info(user.id, user.username, 'sid', 'KILL', 'log', 'broadcast')


class TypeLogs(Enum):
    remote = 'remote'
    console = 'console'
    off = 'off'


class UserLog(BaseModel):
    id: int
    type: TypeLogs


@router.post("/api.v1/user_log")
async def start_user_logs(item: UserLog, authjwt: AuthJWT = Depends()):
    authjwt.jwt_required()
    pk = authjwt.get_jwt_subject()
    user = await get_user(pk)
    room = STATIC_USER(pk)
    devices_user = await get_users_session_for_room(STATIC_USER(item.id))
    await sio.emit('remoteLog', {"type": item.type.value}, room=devices_user[0].sid)
    logger.info(user.id, user.username, 'sid', 'START', 'user_log', room)
