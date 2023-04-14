import asyncio
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func, cast, Boolean, case, String, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from chat.models.dialog import DialogParticipant
from clients.models import Device
from clients.schema import DeviceUserChat
from shared.db import async_session
from sso.models.user import User


async def get_users_for_admin() -> List[DeviceUserChat]:
    """ Получение пользователей для админа"""
    async with async_session() as session:
        try:
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
            return [DeviceUserChat(
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


async def get_user_for_admin(user_id: int) -> Optional[DeviceUserChat]:
    """ Получение пользователей для админа"""
    async with async_session() as session:
        device_query = (
            select(
                Device.is_mobile,
                Device.is_connected,
                Device.updated_at,
                Device.model,
                Device.os,
            )
            .where(Device.user_id == user_id)
            .order_by(
                desc(Device.is_connected),
                desc(Device.updated_at)
            )
            .limit(1)
        )
        user_query = (
            select(
                User.username,
                User.id,
            )
            .where(User.id == user_id)
        )
        device_result, user_result = await asyncio.gather(
            session.execute(device_query),
            session.execute(user_query)
        )
        device_row = device_result.fetchone()
        user_row = user_result.fetchone()
        if user_row is None or device_row is None:
            return None
        return DeviceUserChat(
            name=user_row.username,
            id=user_row.id,
            lastVisit=datetime.isoformat(device_row[2]) if device_row[2] is not None else None,
            isConnected=device_row.is_connected,
            deviceModel=device_row.os,
            isMobile=device_row.is_mobile
        )


query_device_online = (
    # Подзапрос для выбора последнего онлайн-устройства или устройства с наибольшей датой обновления
    select(
        Device.user_id,
        func.max(Device.updated_at).label('last_updated_at')
    )
    .where(Device.is_connected.isnot(False))
    .group_by(Device.user_id)
    .subquery()
)
