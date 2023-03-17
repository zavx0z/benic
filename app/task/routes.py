from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from task.crud import create_task, get_task, update_task, delete_task
from task.schema import TaskCreate, TaskUpdate, TaskInDBBase
from shared.db import get_async_session

router = APIRouter()


@router.post("/", response_model=TaskInDBBase)
async def create_new_task(task: TaskCreate, app_id: int, owner_id: int, session: AsyncSession = Depends(get_async_session)):
    return await create_task(session=session, task_create=task, app_id=app_id, owner_id=owner_id)


@router.get("/{task_id}", response_model=TaskInDBBase)
async def read_task(task_id: int, session: AsyncSession = Depends(get_async_session)):
    db_task = await get_task(session=session, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=TaskInDBBase)
async def update_existing_task(task_id: int, task: TaskUpdate, session: AsyncSession = Depends(get_async_session)):
    db_task = await get_task(session=session, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return await update_task(session=session, task=db_task, task_update=task)


@router.delete("/{task_id}", response_model=None)
async def delete_existing_task(task_id: int, session: AsyncSession = Depends(get_async_session)):
    db_task = await get_task(session=session, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_task(session=session, task_id=db_task.id)
