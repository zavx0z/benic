from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth.models import User
from src.shared.db import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Определяем объект контекста для шифрования паролей


class Item(BaseModel):
    username: str
    password: str


async def create_user(db: Session, item: Item):
    """Создание нового пользователя"""
    async with db.begin():  # Проверяем, что пользователь с таким именем еще не зарегистрирован
        result = await db.execute(User.__table__.select().where(User.username == item.username))
        user = result.fetchone()
    if user:
        raise HTTPException(status_code=400, detail="User already registered")
    hashed_password = pwd_context.hash(item.password)  # Шифруем пароль
    user = User(username=item.username, hashed_password=hashed_password)  # Создаем нового пользователя
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}


@router.post("/api.v1/join")
async def register(item: Item, db=Depends(get_db)):
    """Регистрация нового пользователя"""
    return create_user(db, item)
