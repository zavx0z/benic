from client.schema import DeviceClientSchema


def device_from_client(data: dict) -> DeviceClientSchema:
    device_info = DeviceClientSchema(
        user_agent=data.get('userAgent', data.get('ua')),
        is_mobile=data.get('isMobile', False),
        vendor=data.get('vendor'),
        model=data.get('model', ''),
        os=data.get('osName', data.get('os')),
        os_version=data.get('osVersion'),
    )
    return device_info
