from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models import Server
from server.schema import ServerCreate, ServerUpdate, ServerInDB


async def create_server(session: AsyncSession, server_create: ServerCreate) -> ServerInDB:
    server = Server(
        name=server_create.name,
        description=server_create.description,
        hostname=server_create.hostname,
        port=server_create.port,
        username=server_create.username,
        password=server_create.password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(server)
    await session.commit()
    await session.refresh(server)
    return server


async def get_server(session: AsyncSession, server_id: int) -> Optional[ServerInDB]:
    result = await session.execute(select(Server).filter_by(id=server_id))
    server = result.scalars().first()
    return server


async def update_server(session: AsyncSession, server: ServerInDB, server_update: ServerUpdate) -> ServerInDB:
    server.name = server_update.name
    server.description = server_update.description
    server.hostname = server_update.hostname
    server.port = server_update.port
    server.username = server_update.username
    server.password = server_update.password
    server.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(server)
    return server


async def delete_server(session: AsyncSession, server_id: int) -> None:
    result = await session.execute(select(Server).filter_by(id=server_id))
    server = result.scalars().first()
    if server:
        session.delete(server)
        await session.commit()
