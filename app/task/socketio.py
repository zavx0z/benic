from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db import get_async_session
from shared.socketio import sio
from task.crud import get_task, update_task, create_task


@sio.on('create_task')
async def create_task_handler(sid, task_create, app_id, session: AsyncSession = Depends(get_async_session)):
    user = await sio.get_session(sid)
    if not user:
        await sio.emit('error', {"message": "Ошибка аутентификации.", "type": "warning"}, room=sid)
        return
    task = await create_task(session, task_create, app_id=app_id, owner_id=user.id)
    await sio.emit('task_created', task, room=sid)


@sio.on('get_task')
async def get_task_handler(sid, task_id, session: AsyncSession = Depends(get_async_session)):
    user = await sio.get_session(sid)
    if not user:
        await sio.emit('error', {"message": "Ошибка аутентификации.", "type": "warning"}, room=sid)
        return
    task = await get_task(session, task_id)
    if not task:
        await sio.emit('error', {"message": "Задача не найдена.", "type": "warning"}, room=sid)
        return
    await sio.emit('task_fetched', task, room=sid)


@sio.on('update_task')
async def update_task_handler(sid, task_id, task_update, session: AsyncSession = Depends(get_async_session)):
    user = await sio.get_session(sid)
    if not user:
        await sio.emit('error', {"message": "Ошибка аутентификации.", "type": "warning"}, room=sid)
        return
    task = await get_task(session, task_id)
    if not task:
        await sio.emit('error', {"message": "Задача не найдена.", "type": "warning"}, room=sid)
        return
    updated_task = await update_task(session, task, task_update)
    await sio.emit('task_updated', updated_task, room=sid)
