from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError

from auth.models import Device
from auth.schema.device import DeviceBase
from shared.db import async_session


async def add_user_device(user_id: int, device: DeviceBase):
    """
    Добавляет новое устройство для пользователя, если оно еще не существует.
    """
    async with async_session() as session:
        # Ищем устройство в базе данных, используя параметры
        device_inst = await session.execute(select(Device).filter_by(
            is_mobile=device.is_mobile,
            vendor=device.vendor,
            model=device.model,
            os=device.os,
            os_version=device.os_version,
            user_agent=device.user_agent,
            user_id=user_id
        ))
        # Извлекаем результат запроса
        device_inst = device_inst.scalar()
        # Если устройство не найдено, создаем новое и добавляем его в базу данных
        if device_inst is None:
            device_inst = Device(
                is_mobile=device.is_mobile,
                vendor=device.vendor,
                model=device.model,
                os=device.os,
                os_version=device.os_version,
                user_agent=device.user_agent,
                user_id=user_id,
                updated_at=None,
                is_connected=None
            )
            try:
                session.add(device_inst)
                await session.commit()
            except IntegrityError:
                # Обрабатываем ошибки базы данных
                await session.rollback()
                raise
        # Если устройство найдено, обновляем его поля
        else:
            device_inst.is_connected = True
            await session.commit()
        # Возвращаем найденное или созданное устройство
        return device_inst


async def update_device_status(user_id: int, device_id: int, is_connected: bool):
    """
    Обновляет статус подключения устройства.
    """
    async with async_session() as session:
        # Обновляем статус устройства
        stmt = (
            update(
                Device
            )
            .where(Device.id == device_id)
            .values(is_connected=is_connected)
        )
        await session.execute(stmt)
        await session.commit()
        # Получаем обновленное устройство из базы данных
        device = await session.get(Device, device_id)
        return device


async def get_connected_devices(user_id: int):
    """
    Возвращает все устройства пользователя со статусом подключения True.
    """
    async with async_session() as session:
        # Запрашиваем устройства пользователя со статусом True
        devices = await session.execute(
            select(Device).where(and_(Device.user_id == user_id, Device.is_connected == True))
        )
        # Извлекаем результат запроса
        devices = devices.scalars().all()
        return devices
