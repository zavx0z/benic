from typing import Optional

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    senderId: int
    created: str
    text: str
    read: Optional[bool]
