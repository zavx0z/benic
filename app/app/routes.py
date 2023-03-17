from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_app, get_app, update_app, delete_app
from app.schema import AppCreate, AppUpdate, AppDB
from shared.db import get_async_session

router = APIRouter()


@router.post("/", response_model=AppDB)
async def create_new_app(app: AppCreate, session: AsyncSession = Depends(get_async_session)):
    return await create_app(session=session, app_create=app)


@router.get("/{app_id}", response_model=AppDB)
async def read_app(app_id: int, session: AsyncSession = Depends(get_async_session)):
    db_app = await get_app(session=session, app_id=app_id)
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return db_app


@router.put("/{app_id}", response_model=AppDB)
async def update_existing_app(app_id: int, app: AppUpdate, session: AsyncSession = Depends(get_async_session)):
    db_app = await get_app(session=session, app_id=app_id)
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return await update_app(session=session, app=db_app, app_update=app)


@router.delete("/{app_id}", response_model=None)
async def delete_existing_app(app_id: int, session: AsyncSession = Depends(get_async_session)):
    db_app = await get_app(session=session, app_id=app_id)
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    await delete_app(session=session, app_id=db_app.id)
