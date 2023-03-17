import enum

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.types import Enum


class ServerType(enum.Enum):
    ENVIRONMENT = "environment"
    DATABASE = "database"
    APPLICATION = "application"


class BaseModelServer:
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(50), index=True, nullable=False)
    description = Column(String)
    address = Column(String)
    port = Column(Integer)
    server_type = Column(Enum(ServerType), default=ServerType.APPLICATION, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
