from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.models import User
from src.auth.schema import UserData
from src.shared.db import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Определяем объект контекста для шифрования паролей


async def authenticate_user(username: str, password: str, db):
    """Аутентификации пользователя"""
    stmt = select(User).where(User.username == username)  # create select statement
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):  # check password
        return None

    return user


def create_access_token(data: dict, authjwt: AuthJWT):
    """Генерация токена авторизации"""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authjwt.create_access_token(subject=data["username"], expires_time=expires_delta)
    # return {"access_token": access_token, "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}
    return access_token


async def save_refresh_token(refresh_token: str, db: Session, user: User):
    async with db.begin():  # Сохраняем токен обновления в базе данных
        result = await db.execute(User.__table__.select().where(User.username == user.username))
        user = result.fetchone()
        user.refresh_token = refresh_token
        await db.commit()


class Request(BaseModel):
    username: str
    password: str


@router.post("/api.v1/login")
async def login(item: Request, db=Depends(get_db), authjwt: AuthJWT = Depends()) -> UserData:
    """Аутентификация и выдача токена"""
    user = await authenticate_user(item.username, item.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"username": user.username}, authjwt)  # Генерируем токен авторизации
    refresh_token = authjwt.create_refresh_token(subject=user.username)  # Генерируем токен обновления
    # save_refresh_token(refresh_token, db)
    return UserData(
        id=user.id,
        username=user.username,
        accessToken=access_token,
        refreshToken=refresh_token,
        status=200
    )
