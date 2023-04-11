from pydantic import BaseModel

from sso.models.role import Role


class SessionUser(BaseModel):
    id: int
    username: str
    role: Role
    device_id: int
    sid: str
