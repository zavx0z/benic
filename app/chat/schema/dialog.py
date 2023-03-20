from pydantic import BaseModel


class DialogStatistic(BaseModel):
    dialogId: int
    dialogName: str
    totalMessages: int
    unreadMessages: int
    ownerId: int
    ownerName: str
    lastMessageText: str
    lastMessageTime: str



