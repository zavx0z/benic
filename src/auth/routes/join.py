from fastapi import APIRouter, Depends
from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select

from src.auth.models import User
from src.shared.db import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Credentials(BaseModel):
    username: str
    password: str


class ItemUser(BaseModel):
    id: int
    username: str


@router.post("/api.v1/join")
async def register(item: Credentials, db=Depends(get_db)) -> ItemUser:
    """Регистрация нового пользователя"""
    # Проверяем, есть ли пользователь с таким же именем
    stmt = select(User).where(User.username == item.username)
    result = await db.execute(stmt)
    user = result.fetchone()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Создаем нового пользователя
    hashed_password = pwd_context.hash(item.password)
    user = User(username=item.username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ItemUser(id=user.id, username=user.username)
