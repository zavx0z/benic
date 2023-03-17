from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AppBase(BaseModel):
    name: str
    description: Optional[str] = None


class AppCreate(AppBase):
    pass


class AppUpdate(AppBase):
    pass


class AppDB(AppBase):
    id: int
    created_date: datetime
    last_modified_date: datetime

    class Config:
        orm_mode = True
