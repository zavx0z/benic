"""
Для создания моделей для чата необходимо определиться с сущностями, которые будут храниться в базе данных. В случае чата обычно имеются следующие сущности:

Сообщение
Диалог
Участник диалога

В этих моделях:

Модель Message:
 Таблица для хранения сообщений чата.
 Она включает в себя текст сообщения,
 идентификатор отправителя и получателя,
 а также дату и время создания сообщения.
 Связь между отправителем и получателем задается внешним ключом на таблицу пользователей.

Модель Dialog представляет собой таблицу для хранения информации о диалогах.
Она включает в себя имя диалога (опционально) и дату создания диалога.
Связь между участниками диалога задается через таблицу DialogParticipant.

Модель DialogParticipant представляет собой таблицу для хранения информации об участниках диалогов.
Она включает в себя идентификатор пользователя и идентификатор диалога.
Связь между пользователем и диалогом задается через внешние ключи на таблицы User и Dialog.
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id])

    dialog_id = Column(Integer, ForeignKey("dialog.id"), nullable=False)

    def __str__(self):
        return f"{self.sender_id}_{self.text[:10]}"

    def __repr__(self):
        return self.__str__()


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
