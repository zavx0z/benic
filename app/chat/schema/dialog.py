from pydantic import BaseModel


class DialogStatistic(BaseModel):
    dialogId: int
    dialogName: str
    totalMessages: int
    unreadMessages: int
    ownerId: int
    lastMessageText: str
    lastMessageTime: str
    lastMessageSenderId: int



