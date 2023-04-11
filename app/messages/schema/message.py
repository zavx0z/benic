from typing import Optional

from pydantic import BaseModel


class MessageInfo(BaseModel):
    lastMessageSenderId: int
    lastMessageTime: str
    lastMessageText: str


class MessageResponse(BaseModel):
    id: int
    senderId: int
    created: str
    text: str
    read: Optional[bool]
