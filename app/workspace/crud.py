from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from workspace.models import Workspace
from workspace.schema import WorkspaceCreate, WorkspaceUpdate, WorkspaceInDB


async def create_workspace(session: AsyncSession, workspace_create: WorkspaceCreate) -> WorkspaceInDB:
    workspace = Workspace(
        name=workspace_create.name,
        description=workspace_create.description,
    )
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)
    return workspace


async def get_workspace(session: AsyncSession, workspace_id: int) -> Optional[WorkspaceInDB]:
    result = await session.execute(select(Workspace).filter_by(id=workspace_id))
    workspace = result.scalars().first()
    return workspace


async def get_workspaces(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[WorkspaceInDB]:
    result = await session.execute(select(Workspace).offset(skip).limit(limit))
    workspaces = result.scalars().all()
    return workspaces


async def update_workspace(session: AsyncSession, workspace: WorkspaceInDB, workspace_update: WorkspaceUpdate) -> WorkspaceInDB:
    workspace.name = workspace_update.name
    workspace.description = workspace_update.description
    workspace.last_modified_date = datetime.utcnow()
    await session.commit()
    await session.refresh(workspace)
    return workspace


async def delete_workspace(session: AsyncSession, workspace_id: int) -> None:
    result = await session.execute(select(Workspace).filter_by(id=workspace_id))
    workspace = result.scalars().first()
    if workspace:
        session.delete(workspace)
        await session.commit()
