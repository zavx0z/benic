from typing import Optional, Union

from pydantic import BaseModel


class SessionUser(BaseModel):
    id: int
    username: str
    is_superuser: bool
    device_id: int
    sid: str


class MessageRequest(BaseModel):
    ownerId: int
    senderId: int
    text: str


class ChatPayload(BaseModel):
    action: str
    data: Optional[Union[dict, int, list]]
