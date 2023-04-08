from datetime import datetime
from typing import List

from sqlalchemy import select, func, cast, Boolean, case, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from auth.models import Device, User
from chat.models.dialog import DialogParticipant
from chat.schema.users import UserChat
from shared.db import async_session


async def get_users_by_dialog_ids(dialog_ids: List[int]) -> List[UserChat]:
    """ Получение состояний пользователей в диалогах в которых они состоят """
    async with async_session() as session:
        try:
            # Подзапрос для выбора последнего онлайн-устройства или устройства с наибольшей датой обновления
            subquery2 = (
                select(
                    Device.user_id,
                    func.max(Device.updated_at).label('last_updated_at')
                )
                .where(Device.is_connected.isnot(False))
                .group_by(Device.user_id)
                .subquery()
            )

            subquery = (
                select(
                    User.id,
                    func.max(cast(Device.is_mobile, String)).label('isMobile'),
                    func.max(Device.updated_at).label('lastVisit'),
                    func.max(cast(Device.is_connected, String)).label('isConnected'),
                    func.max(Device.model).label('deviceModel'),
                    func.max(Device.os).label('deviceOs'),
                    func.row_number().over(
                        partition_by=Device.user_id,
                        order_by=(case((Device.is_connected.is_(True), 1), else_=2), func.max(Device.updated_at).desc())
                    ).label('device_order')
                )
                .where(DialogParticipant.dialog_id.in_(dialog_ids))
                .group_by(User.id, Device.is_connected, Device.user_id)
                .join(DialogParticipant, User.id == DialogParticipant.user_id)
                .join(Device, User.id == Device.user_id)
                .subquery()
            )
            query = (
                select(
                    User,
                    subquery.c.id,
                    subquery.c.lastVisit,
                    cast(subquery.c.isConnected, Boolean).label('isConnected'),
                    subquery.c.deviceModel,
                    subquery.c.deviceOs,
                    cast(subquery.c.isMobile, Boolean).label('isMobile'),
                )
                .join(subquery, User.id == subquery.c.id)
                .where(subquery.c.device_order == 1)
                .options(selectinload(User.devices))
            )
            result = await session.execute(query)
            return [UserChat(
                name=str(row[0]),
                id=row[1],
                lastVisit=datetime.isoformat(row[2]) if row[2] is not None else None,
                isConnected=row[3],
                deviceModel=row[5],
                isMobile=row[6]
            ) for row in result.fetchall()]
        except SQLAlchemyError as e:
            # Обработка ошибки
            print(f"An error occurred: {e}")
            return []
