from pydantic import BaseModel


class SessionUser(BaseModel):
    id: int
    username: str
    is_superuser: bool


class MessageRequest(BaseModel):
    ownerId: int
    senderId: int
    text: str
