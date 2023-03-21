from operator import and_
from typing import List, Tuple

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from chat.models.dialog import Dialog, DialogParticipant
from chat.models.message import Message, MessageReaders
from shared.db import async_session


async def create_dialog(name: str, owner_id: int, participant_ids: [int], ):
    """Создание диалога"""
    async with async_session() as session:
        dialog = Dialog(name=name, owner_id=owner_id)
        session.add(dialog)
        await session.flush()
        for participant_id in participant_ids:
            dialog_participant = DialogParticipant(user_id=participant_id, dialog_id=dialog.id)
            session.add(dialog_participant)
        await session.commit()
        await session.refresh(dialog)
    return dialog


async def get_dialog_by_id(dialog_id: int):
    """Получение диалога по ID"""
    async with async_session() as session:
        result = await session.execute(
            select(Dialog)
            .filter_by(id=dialog_id)
            .options(
                selectinload(Dialog.participants)
                .selectinload(DialogParticipant.user)
            )
        )
        dialog = result.scalar_one_or_none()
        await session.close()
    return dialog


async def get_dialogs_by_user_id_and_name(user_id: int, dialog_name: str):
    """Получение диалога по ID пользователя и имени диалога"""
    async with async_session() as session:
        stmt = (
            select(Dialog)
            .join(DialogParticipant)
            .filter(DialogParticipant.user_id == user_id)
            .filter(Dialog.name == dialog_name)
            .options(selectinload(Dialog.participants).selectinload(DialogParticipant.user))
        )
        result = await session.execute(stmt)
        dialogs = result.scalars().all()
        return dialogs


class DialogDB(BaseModel):
    dialog_id: int
    owner_id: int
    username: str

    class Config:
        orm_mode = True


async def get_participant_dialogs(user_id: int):
    """Получение всех диалогов пользователя где он является участником по ID пользователя"""
    async with async_session() as session:
        stmt = (
            select(Dialog)
            .join(DialogParticipant)
            .filter(DialogParticipant.user_id == user_id)
            .options(
                selectinload(Dialog.participants)
                .selectinload(DialogParticipant.user)
            )
        )
        result = await session.execute(stmt)
        dialogs = result.scalars().all()
        return dialogs


async def get_dialogs_by_user_id(session: AsyncSession, user_id: int) -> List[Tuple[int, int, str]]:
    """Получение диалогов по ID пользователя"""
    result = await session.execute(
        select(
            Dialog.id,
            Dialog.name,
            Dialog.owner_id,
            User.username
        )
        .join(User, Dialog.owner_id == User.id)
        .join(DialogParticipant, DialogParticipant.user_id == user_id)
        .group_by(Dialog.id, User.username)
    )
    return result.fetchall()


async def get_dialog_last_message(session: AsyncSession, dialog_ids: List[int]):
    subquery = (
        select(
            Message.dialog_id,
            func.max(Message.created_at).label('max_created_at')
        )
        .filter(Message.dialog_id.in_(dialog_ids))
        .group_by(Message.dialog_id)
        .subquery()
    )
    result = await session.execute(
        select(
            Message.dialog_id,
            Message.text,
            Message.created_at
        )
        .join(subquery, and_(
            Message.dialog_id == subquery.c.dialog_id,
            Message.created_at == subquery.c.max_created_at
        ))
        .filter(Message.dialog_id.in_(dialog_ids))
    )
    return result.fetchall()


async def get_all_message_count_for_dialogs(session: AsyncSession, dialog_ids: List[int]) -> List[Tuple[int, int]]:
    result = await session.execute(
        select(
            Message.dialog_id,
            func.count(Message.id)
        )
        .filter(Message.dialog_id.in_(dialog_ids))
        .group_by(Message.dialog_id)
    )
    return result.fetchall()


async def get_unread_message_count_for_dialogs(session: AsyncSession, dialog_ids: List[int], user_id: int) -> List[Tuple[int, int]]:
    result = await session.execute(
        select(
            Message.dialog_id,
            func.count(MessageReaders.user_id)
        )
        .join(MessageReaders)
        .filter(Message.dialog_id.in_(dialog_ids))
        .filter(Message.sender_id != user_id)
        .filter(MessageReaders.user_id != user_id)
        .group_by(Message.dialog_id)
    )
    return result.fetchall()
