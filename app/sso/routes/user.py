from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import FreshTokenRequired
from sqlalchemy import select

from sso.models.user import User
from sso.schema.user import UserSchema
from shared.db import get_db

router = APIRouter()


@router.get("/api.v1/user")
async def get_user(authjwt: AuthJWT = Depends(), db=Depends(get_db)):
    """Получение информации о текущем пользователе"""
    try:
        authjwt.jwt_required()
        pk = authjwt.get_jwt_subject()
        stmt = select(User).where(User.id == pk)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            return UserSchema(
                id=user.id,
                username=user.username,
                role=user.role.name
            )
    except FreshTokenRequired:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token has expired. Please request a new one using the provided refresh token.", "refresh_url": "/api.v1/refresh"},
        )
