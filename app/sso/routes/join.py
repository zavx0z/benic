from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from fastapi_another_jwt_auth import AuthJWT
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clients.query.async_query import create_device
from events import async_event_manager, DB_CREATE_USER
from shared.db import get_db
from sso.models.role import Role
from sso.models.user import User
from sso.schema.user import UserWithTokenSchema, JoinUserRequest
from sso.token import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
async def register(item: JoinUserRequest, request: Request, db=Depends(get_db), authjwt: AuthJWT = Depends()) -> UserWithTokenSchema:
    """Регистрация нового пользователя"""
    user = await get_user(db, item.username)
    if user:
        raise HTTPException(status_code=401, detail="already registered")
    ip = request.client.host
    user = await create_user(db, item.username, item.password)
    await create_device(user.id, item.device, ip)
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
