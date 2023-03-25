from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserChat(BaseModel):
    id: int
    name: Optional[str]
    isMobile: bool
    lastVisit: Optional[str]
