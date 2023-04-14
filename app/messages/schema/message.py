from pydantic import BaseModel, root_validator


class MessageInfo(BaseModel):
    lastMessageSenderId: int
    lastMessageTime: str
    lastMessageText: str


class MessageResponse(BaseModel):
    id: int
    senderId: int
    created: str
    text: str
    read: bool = False

    @root_validator(pre=True)
    def map_fields(cls, values):
        data = {
            'id': values.get('id'),
            'senderId': values.get('sender_id'),
            'created': values.get('created_at').isoformat(),
            'text': values.get('text'),
            'read': bool(values.get('read') is not None)
        }
        return data
