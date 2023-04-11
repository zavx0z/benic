from clients.schema import DevicePayloadSchema


def device_from_client(data: dict) -> DevicePayloadSchema:
    device_info = DevicePayloadSchema(
        user_agent=data.get('userAgent', data.get('ua')),
        is_mobile=data.get('isMobile', False),
        vendor=data.get('vendor'),
        model=data.get('model', ''),
        os=data.get('osName', data.get('os')),
        os_version=data.get('osVersion'),
        tz=data.get('tz')
    )
    return device_info
