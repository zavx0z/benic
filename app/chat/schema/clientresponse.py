from typing import Optional

from pydantic import BaseModel


class ClientResponse(BaseModel):
    id: int
    username: str
    dialogId: Optional[int]
