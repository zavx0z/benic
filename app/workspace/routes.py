from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from workspace.crud import create_workspace, get_workspace, update_workspace, delete_workspace
from workspace.schema import WorkspaceCreate, WorkspaceUpdate, WorkspaceInDB
from shared.db import get_async_session

router = APIRouter()


@router.post("/", response_model=WorkspaceInDB)
async def create_new_workspace(workspace: WorkspaceCreate, session: AsyncSession = Depends(get_async_session)):
    return await create_workspace(session=session, workspace_create=workspace)


@router.get("/{workspace_id}", response_model=WorkspaceInDB)
async def read_workspace(workspace_id: int, session: AsyncSession = Depends(get_async_session)):
    db_workspace = await get_workspace(session=session, workspace_id=workspace_id)
    if db_workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db_workspace


@router.put("/{workspace_id}", response_model=WorkspaceInDB)
async def update_existing_workspace(workspace_id: int, workspace: WorkspaceUpdate, session: AsyncSession = Depends(get_async_session)):
    db_workspace = await get_workspace(session=session, workspace_id=workspace_id)
    if db_workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return await update_workspace(
        session=session,
        workspace=db_workspace,
        workspace_update=workspace
    )


@router.delete("/{workspace_id}", response_model=None)
async def delete_existing_workspace(workspace_id: int, session: AsyncSession = Depends(get_async_session)):
    db_workspace = await get_workspace(session=session, workspace_id=workspace_id)
    if db_workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    await delete_workspace(session=session, workspace_id=db_workspace.id)
