from fastapi import APIRouter, Depends
from fastapi_another_jwt_auth import AuthJWT

router = APIRouter()


@router.post("/api.v1/refresh")
async def refresh(authjwt: AuthJWT = Depends()):
    """Обновление токена авторизации"""
    authjwt.jwt_refresh_token_required()  # Получаем имя пользователя из токена обновления
    username = authjwt.get_jwt_subject()  # Генерируем новый токен авторизации
    access_token = authjwt.create_access_token(subject=username)
    return {"access_token": access_token}
