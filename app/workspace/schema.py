from typing import Optional

from pydantic import BaseModel


# Properties to receive via API on creation
class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


# Properties to receive via API on update
class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Properties shared by models stored in DB
class WorkspaceInDBBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties stored in DB
class WorkspaceInDB(WorkspaceInDBBase):
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None
