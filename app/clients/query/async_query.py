from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError

from clients.models import Device
from clients.schema import DevicePayloadSchema
from shared.db import async_session


async def create_device(user_id: int, data: DevicePayloadSchema, ip: str):
    async with async_session() as session:
        device = Device(
            is_mobile=data.is_mobile,
            is_tablet=data.is_tablet,
            is_browser=data.is_browser,
            vendor=data.vendor,
            model=data.model,
            os=data.os,
            os_version=data.os_version,
            user_agent=data.user_agent,
            user_id=user_id,
            updated_at=None,
            is_connected=True,
            ip=ip,
            tz=data.tz,
            width=data.width,
            height=data.height,
            resolution=data.resolution,
        )
        try:
            session.add(device)
            await session.commit()
            return device
        except IntegrityError:
            # Обрабатываем ошибки базы данных
            await session.rollback()
            raise


async def get_or_add_user_device(user_id: int, data_device: DevicePayloadSchema, ip: str):
    """
    Добавляет новое устройство для пользователя, если оно еще не существует.
    """
    async with async_session() as session:
        # Ищем устройство в базе данных, используя параметры
        device = await session.execute(select(Device).filter_by(
            is_mobile=data_device.is_mobile,
            is_tablet=data_device.is_tablet,
            is_browser=data_device.is_browser,
            vendor=data_device.vendor,
            model=data_device.model,
            os=data_device.os,
            os_version=data_device.os_version,
            user_agent=data_device.user_agent,
            user_id=user_id,
            width=data_device.width,
            height=data_device.height,
            resolution=data_device.resolution,
        ))
        # Извлекаем результат запроса
        device = device.scalar()
        # Если устройство не найдено, создаем новое и добавляем его в базу данных
        if device is None:
            device = await create_device(user_id, data_device, ip)
        # Если устройство найдено, обновляем его поля
        else:
            device.ip = ip
            # if data_device.tz:
            device.tz = data_device.tz
            device.is_connected = True
            await session.commit()
        # Возвращаем найденное или созданное устройство
        return device


async def update_device_status(user_id: int, device_id: int, is_connected: bool):
    """
    Обновляет статус подключения устройства.
    """
    async with async_session() as session:
        await session.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(is_connected=is_connected)
        )
        await session.commit()
        # Получаем обновленное устройство из базы данных
        device = await session.get(Device, device_id)
        return device


async def update_device_notification_token(device_id: int, notification_token: str):
    """
    Обновляет токен firebase.
    """
    async with async_session() as session:
        await session.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(notification_token=notification_token)
        )
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
