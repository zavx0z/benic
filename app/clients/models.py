from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey
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
    notification_token = Column(String(256), nullable=True)
    ip = Column(String(50), nullable=True)
    tz = Column(String(50), nullable=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="devices")

    def __str__(self):
        return f"<{self.os}>"

    def __repr__(self):
        return self.__str__()
