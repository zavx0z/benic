from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ServerBase(BaseModel):
    name: str
    description: Optional[str] = None
    hostname: str
    port: int
    username: str
    password: str


class ServerCreate(ServerBase):
    pass


class ServerUpdate(ServerBase):
    pass


class ServerInDBBase(ServerBase):
    id: int

    class Config:
        orm_mode = True


class ServerInDB(ServerInDBBase):
    created_at: datetime
    updated_at: datetime


class Server(ServerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
