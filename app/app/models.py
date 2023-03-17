from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.models.app import BaseModelApp
from server.models import Server
from shared import Base


class App(Base, BaseModelApp):
    __tablename__ = "app"
    servers = relationship("ServerAppAssociation", back_populates="app")
    tasks = relationship("Task", back_populates="app")


class ServerAppAssociation(Base):
    __tablename__ = "server_app_association"
    server_id = Column(Integer, ForeignKey("server.id"), primary_key=True)
    app_id = Column(Integer, ForeignKey("app.id"), primary_key=True)
    server = relationship(Server, back_populates="apps")
    app = relationship(App, back_populates="servers")
