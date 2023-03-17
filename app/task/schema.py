from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from task.models import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    status: Optional[TaskStatus] = TaskStatus.NEW
    app_id: int
    owner_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


class TaskInDBBase(TaskBase):
    id: int
    creation_date: datetime
    last_modified_date: datetime
    completion_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    priority: int
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    status: str
