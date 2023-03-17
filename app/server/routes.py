from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.crud import create_server, get_server, update_server, delete_server
from server.schema import ServerCreate, ServerUpdate, ServerInDBBase
from task.crud import get_task
from workspace.crud import get_workspace
from shared.db import get_async_session

router = APIRouter()


@router.post("/", response_model=ServerInDBBase)
async def create_new_server(server: ServerCreate, workspace_id: int, task_id: int, session: AsyncSession = Depends(get_async_session)):
    workspace = await get_workspace(session=session, workspace_id=workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    task = await get_task(session=session, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return await create_server(session=session, server_create=server, workspace_id=workspace_id, task_id=task_id)


@router.get("/{server_id}", response_model=ServerInDBBase)
async def read_server(server_id: int, session: AsyncSession = Depends(get_async_session)):
    db_server = await get_server(session=session, server_id=server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@router.put("/{server_id}", response_model=ServerInDBBase)
async def update_existing_server(server_id: int, server: ServerUpdate, session: AsyncSession = Depends(get_async_session)):
    db_server = await get_server(session=session, server_id=server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return await update_server(session=session, server=db_server, server_update=server)


@router.delete("/{server_id}", response_model=None)
async def delete_existing_server(server_id: int, session: AsyncSession = Depends(get_async_session)):
    db_server = await get_server(session=session, server_id=server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    await delete_server(session=session, server_id=db_server.id)
