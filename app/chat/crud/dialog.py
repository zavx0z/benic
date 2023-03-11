from sqlalchemy import select
from sqlalchemy.orm import selectinload

from chat.models import Dialog, DialogParticipant
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
        result = await session.execute(select(Dialog).filter_by(id=dialog_id).options(selectinload(Dialog.participants).selectinload(DialogParticipant.user)))
        dialog = result.scalar_one_or_none()
        await session.close()
    return dialog


async def get_dialog_by_user_id_and_name(user_id: int, dialog_name: str):
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
        dialog = result.scalar_one_or_none()
        return dialog


async def get_dialogs_by_user_id(user_id: int):
    """Получение списка диалогов для пользователя"""
    async with async_session() as session:
        query = (
            select(Dialog)
            .join(DialogParticipant)
            .filter(DialogParticipant.user_id == user_id)
        )
        result = await session.execute(query)
        dialogs = result.scalars().all()
        # для каждого диалога делаем дополнительный запрос для получения участников
        for dialog in dialogs:
            query = (
                select(DialogParticipant)
                .filter(DialogParticipant.dialog_id == dialog.id)
                .options(selectinload(DialogParticipant.user))
            )
            result = await session.execute(query)
            participants = result.scalars().all()
            dialog.participants = participants
    return dialogs
