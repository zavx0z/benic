from pydantic.main import BaseModel

from clients.schema import DevicePayloadSchema


class UserSchema(BaseModel):
    id: int
    username: str
    role: str


class UserWithTokenSchema(UserSchema):
    accessToken: str
    refreshToken: str


class JoinUserRequest(BaseModel):
    username: str
    password: str
    device: DevicePayloadSchema
