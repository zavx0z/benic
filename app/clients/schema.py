from typing import Optional

from pydantic import BaseModel, validator


class DevicePayloadSchema(BaseModel):
    user_agent: Optional[str]
    is_mobile: bool = False
    vendor: Optional[str]
    model: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
    tz: Optional[str]


class DeviceUserChat(BaseModel):
    id: int
    name: Optional[str]
    isMobile: bool
    lastVisit: Optional[str]
    isConnected: bool
    deviceModel: Optional[str]

    @validator('deviceModel')
    def check_deviceModel(cls, value):
        if value == 'Ubuntu':
            return 'Linux'
        return value
