from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from server.models import WorkspaceServerAssociation
from shared import Base


class WorkspaceUserAssociation(Base):
    __tablename__ = "workspace_user_association"
    workspace_id = Column(Integer, ForeignKey("workspace.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    user = relationship("User", back_populates="workspaces")
    workspace = relationship("Workspace", back_populates="users")


class Workspace(Base):
    __tablename__ = "workspace"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    creation_date = Column(DateTime, server_default=func.now())
    last_modified_date = Column(DateTime, onupdate=func.now())

    owner = relationship("User")
    owner_id = Column(Integer, ForeignKey("user.id"))
    users = relationship(WorkspaceUserAssociation, back_populates="workspace")
    servers = relationship(WorkspaceServerAssociation, back_populates="workspace")
