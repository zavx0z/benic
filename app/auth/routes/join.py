from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User, Role
from auth.schema.user import UserWithTokenSchema
from auth.token import create_access_token
from events import async_event_manager, DB_CREATE_USER
from shared.db import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Credentials(BaseModel):
    username: str
    password: str


async def get_user(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)  # Проверяем, есть ли пользователь с таким же именем
    result = await db.execute(stmt)
    user = result.fetchone()
    return user


async def create_user(db: AsyncSession, username: str, password: str, role=Role.client):
    hashed_password = pwd_context.hash(password)  # Создаем нового пользователя
    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/api.v1/join")
async def register(item: Credentials, db=Depends(get_db), authjwt: AuthJWT = Depends()) -> UserWithTokenSchema:
    """Регистрация нового пользователя"""
    user = await get_user(db, item.username)
    if user:
        raise HTTPException(status_code=401, detail="already registered")
    user = await create_user(db, item.username, item.password)
    access_token = create_access_token(user.id, authjwt)  # Генерируем токен авторизации
    refresh_token = authjwt.create_refresh_token(subject=user.id)  # Генерируем токен обновления
    await async_event_manager.notify(DB_CREATE_USER, user.id)  # Событие менеджеру
    return UserWithTokenSchema(
        id=user.id,
        username=user.username,
        accessToken=access_token,
        refreshToken=refresh_token,
        role=user.role.name
    )
