from pydantic import BaseModel


class UserData(BaseModel):
    id: int
    username: str
    accessToken: str
    refreshToken: str
