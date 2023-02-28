from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import FreshTokenRequired

router = APIRouter()


@router.get("/api.v1/user")
async def get_user(authjwt: AuthJWT = Depends()):
    """Получение информации о текущем пользователе"""
    try:
        authjwt.jwt_required()
        username = authjwt.get_jwt_subject()
        return {"username": username}
    except FreshTokenRequired:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token has expired. Please request a new one using the provided refresh token.", "refresh_url": "/api.v1/refresh"},
        )
