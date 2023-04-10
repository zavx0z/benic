from firebase_admin import messaging


def send_notification_to_user(device_token, title, message):
    # Создание сообщения
    notification = messaging.Notification(title=title, body=message)
    message = messaging.Message(notification=notification, token=device_token)

    # Отправка сообщения
    response = messaging.send(message)
    return response
