from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from shared import Base


class Device(Base):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    is_mobile = Column(Boolean, default=False, nullable=False)
    vendor = Column(String(50), nullable=True)
    model = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    user_agent = Column(String(256), nullable=True)
    is_connected = Column(Boolean, default=True, nullable=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="devices")


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(length=320), unique=True)

    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner_dialogs = relationship("Dialog", back_populates="owner")
    dialogs = relationship("DialogParticipant", back_populates="user")
    workspaces = relationship("WorkspaceUserAssociation", back_populates="user")

    devices = relationship(Device, back_populates="user")

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.__str__()
