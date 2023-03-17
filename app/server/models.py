from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.models.provider import Provider
from core.models.server import BaseModelServer
from shared import Base


class WorkspaceServerAssociation(Base):
    __tablename__ = 'workspace_server_association'
    workspace_id = Column(Integer, ForeignKey('workspace.id'), primary_key=True)
    server_id = Column(Integer, ForeignKey('server.id'), primary_key=True)
    workspace = relationship("Workspace", back_populates="servers")
    server = relationship("Server", back_populates="workspaces")


class Server(Base, BaseModelServer):
    __tablename__ = "server"

    provider_id = Column(Integer, ForeignKey('provider.id'), primary_key=True)
    provider = relationship(Provider)

    workspaces = relationship("WorkspaceServerAssociation", back_populates="server")
    apps = relationship("ServerAppAssociation", back_populates="server")
