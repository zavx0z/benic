import jwt
from jwt.exceptions import InvalidTokenError

from config import JWT_SECRET_KEY


def is_token_valid(token: str) -> bool:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        # Токен валидный, если он успешно декодирован
        return True
    except InvalidTokenError:
        # Токен невалидный, если декодирование вызывает исключение InvalidTokenError
        return False
