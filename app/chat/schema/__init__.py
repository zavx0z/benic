from typing import Optional, Union

from pydantic import BaseModel


class MessageRequest(BaseModel):
    ownerId: int
    senderId: int
    text: str


class ChatPayload(BaseModel):
    action: str
    data: Optional[Union[dict, int, list]]
