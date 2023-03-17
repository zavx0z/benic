from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.models.server import BaseModelServer
from shared import Base


class ProviderServerAssociation(Base):
    __tablename__ = "provider_server_association"

    provider_id = Column(Integer, ForeignKey("provider.id"), primary_key=True)
    server_resource_id = Column(Integer, ForeignKey("server_resource.id"), primary_key=True)


class ServerResource(Base, BaseModelServer):
    __tablename__ = "server_resource"

    providers = relationship("Provider", secondary="provider_server_association")
