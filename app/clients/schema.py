import logging
from typing import Optional

from pydantic import BaseModel, validator, root_validator

logger = logging.getLogger('device')

class DevicePayloadSchema(BaseModel):
    user_agent: Optional[str]
    is_mobile: bool = False
    is_tablet: bool = False
    is_browser: bool = False
    vendor: Optional[str]
    model: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
    tz: Optional[str]
    width: Optional[int]
    height: Optional[int]
    resolution: Optional[int]

    @root_validator(pre=True)
    def map_fields(cls, values):
        logger.info(str(values))
        return {
            'user_agent': values.get('userAgent', values.get('ua')),
            'is_mobile': values.get('isMobile', False),
            'is_tablet': values.get('isTablet', False),
            'is_browser': values.get('isBrowser', False),
            'vendor': values.get('vendor'),
            'model': values.get('model'),
            'os': values.get('osName', values.get('os')),
            'os_version': values.get('osVersion'),
            'tz': values.get('tz'),
            'width': int(values.get('width')) if values.get('width') else None,
            'height': int(values.get('height')) if values.get('height') else None,
            'resolution': int(values.get('resolution')) if values.get('resolution') else None,
        }


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


class DeviceClientRequest(BaseModel):  # todo optional rm
    isBrowser: bool
    browserMajorVersion: Optional[str]
    browserFullVersion: Optional[str]
    browserName: Optional[str]
    engineName: Optional[str]
    engineVersion: Optional[str]
    osName: Optional[str]
    osVersion: Optional[str]
    userAgent: Optional[str]
    userAgent: Optional[str]
