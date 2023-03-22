from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from shared import Base


class Dialog(Base):
    __tablename__ = "dialog"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    owner = relationship("User", back_populates="owner_dialogs")
    participants = relationship("DialogParticipant", back_populates="dialog")
    messages = relationship("Message", backref='dialog')

    def __str__(self):
        return f"{self.name}_{self.owner_id}"

    def __repr__(self):
        return self.__str__()


class DialogParticipant(Base):
    __tablename__ = "dialog_participant"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="dialogs")

    dialog_id = Column(Integer, ForeignKey("dialog.id"), nullable=False)
    dialog = relationship("Dialog", back_populates="participants")
