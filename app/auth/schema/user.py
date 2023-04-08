from pydantic.main import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str
    role: str


class UserWithTokenSchema(UserSchema):
    accessToken: str
    refreshToken: str
