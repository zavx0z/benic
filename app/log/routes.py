import logging
from dramatiq_abort import abort
from dramatiq_abort.middleware import AbortMode
from fastapi import APIRouter, Depends
from fastapi_another_jwt_auth import AuthJWT

from sso.crud.user import get_user
from worker import get_running_tasks, tail_logs

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

