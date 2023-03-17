from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task.models import Task
from task.schema import TaskUpdate, TaskCreate, TaskInDBBase


async def create_task(session: AsyncSession, task_create: TaskCreate, app_id: int, owner_id: int) -> TaskInDBBase:
    task = Task(
        name=task_create.name,
        description=task_create.description,
        priority=task_create.priority,
        status=task_create.status,
        app_id=app_id,
        owner_id=owner_id
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(session: AsyncSession, task_id: int) -> Optional[TaskInDBBase]:
    result = await session.execute(select(Task).filter_by(id=task_id))
    task = result.scalars().first()
    return task


async def update_task(session: AsyncSession, task: TaskInDBBase, task_update: TaskUpdate) -> TaskInDBBase:
    task.name = task_update.name
    task.description = task_update.description
    task.priority = task_update.priority
    task.status = task_update.status
    task.last_modified_date = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: int) -> None:
    result = await session.execute(select(Task).filter_by(id=task_id))
    task = result.scalars().first()
    if task:
        session.delete(task)
        await session.commit()
