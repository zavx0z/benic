from typing import Optional, Union

from pydantic import BaseModel

from sso.models import Role


class SessionUser(BaseModel):
    id: int
    username: str
    role: Role
    device_id: int
    sid: str


class MessageRequest(BaseModel):
    ownerId: int
    senderId: int
    text: str


class ChatPayload(BaseModel):
    action: str
    data: Optional[Union[dict, int, list]]
