from auth.schema.device import DeviceBase


def user_device_from_header_auth(user_id, auth):
    data = auth.get('device')
    device_info = DeviceBase(
        user_agent=data.get('userAgent', data.get('ua')),
        is_mobile=data.get('isMobile', False),
        vendor=data.get('vendor'),
        model=data.get('model', ''),
        os=data.get('osName', data.get('os')),
        os_version=data.get('osVersion'),
    )
    return device_info


def get_access_token(sid, auth, environ):
    """Получает токен доступа из авторизации клиента."""
    if auth:
        access_token = auth.get('token')
    elif environ.get('HTTP_AUTHORIZATION'):
        access_token = environ.get('HTTP_AUTHORIZATION').split(' ')[1]
    else:
        return None
    return access_token
