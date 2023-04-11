import logging

import dramatiq

from chat.query.sync_query_dialog import get_clients_not_currently_in_dialog
from clients.query.sync_query import get_or_add_user_device, update_device_notification_token
from clients.utils import device_from_client
from notifications.utils import send_notification_to_user
from worker import session

logger = logging.getLogger('notification')


@dramatiq.actor(max_retries=4)
def notification_subscribe(user_id, device_payload, token):
    device_client = device_from_client(device_payload)
    device_db = get_or_add_user_device(session, user_id, device_client)
    if token != device_db.notification_token:
        device = update_device_notification_token(session, device_db.id, token)
        response = send_notification_to_user(device.notification_token, 'Botswork', 'Вы подписаны на оповещения.')
        logger.info(f"Подписка: {response}")
    else:
        logger.info('Уже подписан')


@dramatiq.actor(max_retries=4)
def notification_clients_not_currently_in_dialog(dialog_id, sender_id, sender_name, current_clients, message):
    tokens = get_clients_not_currently_in_dialog(session, dialog_id, sender_id, current_clients)
    if tokens:
        for token in tokens:
            response = send_notification_to_user(token, sender_name, message)
            logger.info(f"Сообщение: {response}")
    else:
        logger.info('Нет токенов клиентов не в диалоге')
