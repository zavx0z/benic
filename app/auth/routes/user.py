from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import FreshTokenRequired
from pydantic.main import BaseModel
from sqlalchemy import select

from app.auth.models import User
from src import get_db

router = APIRouter()


class ItemUser(BaseModel):
    id: int
    username: str


@router.get("/api.v1/user")
async def get_user(authjwt: AuthJWT = Depends(), db=Depends(get_db)):
    """Получение информации о текущем пользователе"""
    try:
        authjwt.jwt_required()
        username = authjwt.get_jwt_subject()
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalars().first()
        return ItemUser(
            id=user.id,
            username=username
        )
    except FreshTokenRequired:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token has expired. Please request a new one using the provided refresh token.", "refresh_url": "/api.v1/refresh"},
        )
