from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    ownerId: int
    senderId: int
    created: str
    text: str
