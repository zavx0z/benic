from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from clients.models import Device
from clients.schema import DevicePayloadSchema
from sso.models.user import User


def get_or_add_user_device(session: Session, user_id: int, data_device: DevicePayloadSchema):
    """
    Добавляет новое устройство для пользователя, если оно еще не существует.
    """
    # Ищем устройство в базе данных, используя параметры
    device = session.query(Device).filter_by(
        is_mobile=data_device.is_mobile,
        vendor=data_device.vendor,
        model=data_device.model,
        os=data_device.os,
        os_version=data_device.os_version,
        user_agent=data_device.user_agent,
        user_id=user_id
    ).first()
    # Если устройство не найдено, создаем новое и добавляем его в базу данных
    if device is None:
        device = Device(
            is_mobile=data_device.is_mobile,
            vendor=data_device.vendor,
            model=data_device.model,
            os=data_device.os,
            os_version=data_device.os_version,
            user_agent=data_device.user_agent,
            user_id=user_id,
            updated_at=None,
            is_connected=None
        )
        try:
            session.add(device)
            session.commit()
        except IntegrityError:
            # Обрабатываем ошибки базы данных
            session.rollback()
            raise
    # Если устройство найдено, обновляем его поля
    else:
        device.is_connected = True
        session.commit()
    # Возвращаем найденное или созданное устройство
    return device


def update_device_notification_token(session: Session, device_id: int, notification_token: str):
    """
    Обновляет токен firebase.
    """
    # Обновляем токен firebase в базе данных
    try:
        device = session.query(Device).filter_by(id=device_id).update(
            {"notification_token": notification_token}
        )
        session.commit()
    except IntegrityError:
        # Обрабатываем ошибки базы данных
        session.rollback()
        raise
    # Получаем обновленное устройство из базы данных
    device = session.query(Device).get(device_id)
    return device
