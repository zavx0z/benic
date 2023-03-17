from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import App
from app.schema import AppCreate, AppUpdate, AppDB


async def create_app(session: AsyncSession, app_create: AppCreate) -> AppDB:
    app = App(**app_create.dict())
    session.add(app)
    await session.commit()
    await session.refresh(app)
    return app


async def get_apps(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[AppDB]:
    result = await session.execute(select(App).offset(skip).limit(limit))
    apps = result.scalars().all()
    return apps


async def get_app(session: AsyncSession, app_id: int) -> Optional[AppDB]:
    result = await session.execute(select(App).filter_by(id=app_id))
    app = result.scalars().first()
    return app


async def update_app(session: AsyncSession, app: AppDB, app_update: AppUpdate) -> AppDB:
    app_data = app.dict()
    update_data = app_update.dict(exclude_unset=True)
    for field in app_data:
        if field in update_data:
            setattr(app, field, update_data[field])
    await session.commit()
    await session.refresh(app)
    return app


async def delete_app(session: AsyncSession, app_id: int) -> None:
    result = await session.execute(select(App).filter_by(id=app_id))
    app = result.scalars().first()
    if app:
        session.delete(app)
        await session.commit()
