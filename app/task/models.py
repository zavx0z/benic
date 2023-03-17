import enum

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from app.models import App
from core.models.task import BaseModelTask
from shared import Base


class TaskStatus(enum.Enum):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELED = 'canceled'


class TaskPriority(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class Task(Base, BaseModelTask):
    __tablename__ = "task"

    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.NEW, nullable=False)

    app_id = Column(Integer, ForeignKey("app.id"))
    app = relationship(App, back_populates="tasks")
