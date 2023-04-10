import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship

from chat.models.dialog import DialogParticipant, Dialog
from client.models import Device
from shared import Base
from workspace.models import WorkspaceUserAssociation


class Role(enum.Enum):
    client = 1
    developer = 2
    bot = 4
    moderator = 5
    admin = 8
    superuser = 10


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(length=320), unique=True)

    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner_dialogs = relationship(Dialog, back_populates="owner")
    dialogs = relationship(DialogParticipant, back_populates="user")
    workspaces = relationship(WorkspaceUserAssociation, back_populates="user")

    devices = relationship(Device, back_populates="user")

    # Поле roles в виде перечисления (enum)
    role = Column(Enum(Role), default=Role.client, nullable=False)

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.__str__()
