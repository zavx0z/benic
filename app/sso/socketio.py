def get_access_token(sid, auth, environ):
    """Получает токен доступа из авторизации клиента socketio."""
    if auth:
        access_token = auth.get('token')
    elif environ.get('HTTP_AUTHORIZATION'):
        access_token = environ.get('HTTP_AUTHORIZATION').split(' ')[1]
    else:
        return None
    return access_token
