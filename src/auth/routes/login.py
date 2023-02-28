from datetime import timedelta, datetime
from select import select

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic import BaseModel

from src.auth.models import User
from src.shared.db import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Определяем объект контекста для шифрования паролей


class Item(BaseModel):
    username: str
    password: str


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
    expires_delta = timedelta(minutes=authjwt.get_settings().authjwt_access_token_expire_minutes)
    access_token = authjwt.create_access_token(subject=data["username"], expires_time=datetime.utcnow() + expires_delta)
    return {"access_token": access_token, "expires_in": authjwt.get_settings().authjwt_access_token_expire_minutes * 60}


@router.post("/api.v1/login")
async def login(item: Item, db=Depends(get_db), authjwt: AuthJWT = Depends()):
    """Аутентификация и выдача токена"""
    user = await authenticate_user(item.username, item.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"username": user.username}, authjwt)  # Генерируем токен авторизации
    refresh_token = authjwt.create_refresh_token(subject=user.username)  # Генерируем токен обновления
    async with db.begin():  # Сохраняем токен обновления в базе данных
        result = await db.execute(User.__table__.select().where(User.username == user.username))
        user = result.fetchone()
        user.refresh_token = refresh_token
        await db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token}
