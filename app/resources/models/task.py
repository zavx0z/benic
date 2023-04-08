from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.models.task import BaseModelTask
from shared import Base


class TaskResource(Base, BaseModelTask):
    __tablename__ = "task_resource"
    app_resource_id = Column(Integer, ForeignKey("app_resource.id"))
    app = relationship("AppResource", back_populates="tasks")
