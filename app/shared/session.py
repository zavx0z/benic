from enum import Enum

from pydantic import BaseModel


class SessionUser(BaseModel):
    id: int
    username: str
    role: Enum
    device_id: int
    sid: str
