"""
Для создания моделей для чата необходимо определиться с сущностями, которые будут храниться в базе данных. В случае чата обычно имеются следующие сущности:

Сообщение
Диалог
Участник диалога

В этих моделях:

Модель Message представляет собой таблицу для хранения сообщений чата. Она включает в себя текст сообщения, идентификатор отправителя и получателя, а также дату и время создания сообщения. Связь между отправителем и получателем задается внешним ключом на таблицу пользователей.
Модель Dialog представляет собой таблицу для хранения информации о диалогах. Она включает в себя имя диалога (опционально) и дату создания диалога. Связь между участниками диалога задается через таблицу DialogParticipant.
Модель DialogParticipant представляет собой таблицу для хранения информации об участниках диалогов. Она включает в себя идентификатор пользователя и идентификатор диалога. Связь между пользователем и диалогом задается через внешние ключи на таблицы User и Dialog.
Эти модели могут быть использованы для создания таблиц в базе данных, которые хранят информацию о сообщениях, диалогах и участниках диалогов в чате.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from shared import Base


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True)
    text = Column(String(length=1000), nullable=False)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class Dialog(Base):
    __tablename__ = "dialog"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    participants = relationship("DialogParticipant", back_populates="dialog")
    messages = relationship("Message", back_populates="dialog")


class DialogParticipant(Base):
    __tablename__ = "dialog_participant"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    dialog_id = Column(Integer, ForeignKey("dialog.id"), nullable=False)

    user = relationship("User")
    dialog = relationship("Dialog", back_populates="participants")
