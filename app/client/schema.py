from typing import Optional

from pydantic import BaseModel


class DeviceClientSchema(BaseModel):
    user_agent: Optional[str]
    is_mobile: bool = False
    vendor: Optional[str]
    model: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
