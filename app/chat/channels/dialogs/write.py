import logging

from chat.actions import UPDATE, WRITE
from chat.channels import CHANNEL_DIALOG, DYNAMIC_DIALOG, STATIC_DIALOG
from chat.crud.dialog import get_dialog_by_id, get_messages_count
from chat.crud.message import create_message
from chat.models.message import Message
from chat.schema import SessionUser
from chat.schema.message import MessageResponse, MessageInfo
from shared.socketio.connect import sio

logger = logging.getLogger('action')


async def send_msg_info_to_dialog_participants(user: SessionUser, dialog_id: int, message: Message):
    """Рассылка информации о переданном сообщении всем участникам диалога

    (для установки последнего сообщения и увеличения счетчика)
    """
    room = STATIC_DIALOG(dialog_id)
    data_info = MessageInfo(
        lastMessageSenderId=message.sender_id,
        lastMessageTime=message.created_at.isoformat(),
        lastMessageText=message.text[:min(len(message.text), 40)]
    )
    await sio.emit(event=CHANNEL_DIALOG, room=room, data={
        'action': UPDATE,
        "data": {
            "dialogId": dialog_id,
            "message": dict(data_info)
        }})
    logger.info(user.id, user.username, user.sid, UPDATE, CHANNEL_DIALOG, room)


async def send_msg_detail_to_dialog_participants(user: SessionUser, dialog_id: int, message: Message):
    """ Рассылка переданного сообщения участникам которые в текущий момент находятся в диалоге

    1. Собеседникам в диалоге
    2. Себе (для подтверждения получения и обновления времени и id сообщения/отправитель может быть и на других устройствах под другим sid)
    """
    room = DYNAMIC_DIALOG(dialog_id)
    data_message = MessageResponse(
        id=message.id,
        senderId=message.sender_id,
        created=message.created_at.isoformat(),
        text=message.text,
        read=False
    )
    await sio.emit(event=CHANNEL_DIALOG, room=room, data={
        'action': WRITE,
        "data": {
            "dialogId": dialog_id,
            "message": dict(data_message)
        }})
    logger.info(user.id, user.username, user.sid, WRITE, CHANNEL_DIALOG, room)


async def receiving_message(user, dialog_id, text):
    """Прием сообщения.

    - если сообщение от пользователя и это первое сообщение принадлежащее ему - подключаем админов
    - сохранение
    - рассылка информации
    - рассылка сообщения
    """
    dialog = await get_dialog_by_id(dialog_id)
    if 'subscribe' == dialog.name and not user.is_superuser:
        count_messages = await get_messages_count(dialog_id)
        if count_messages == 2:
            pass
            # await sio.emit('clients', dict(ClientResponse(id=user.id, username=user.username, dialogId=dialog_id)))
            # dialog_participants = await get_users_by_dialog_ids([dialog_id])
            # participant = next(filter(lambda inst: inst.id == user.id, dialog_participants), None)
            # room = STATIC_USERS(1)
            # await sio.emit(
            #     event=CHANNEL_USERS,
            #     room=room,
            #     data={
            #         "action": 'add',
            #         "data": dict(participant),
            #     })
            # logger.info(user.id, user.username, user.sid, 'add', CHANNEL_USERS, room)

    message = await create_message(text=text, sender_id=user.id, dialog_id=dialog.id)

    await send_msg_detail_to_dialog_participants(user, dialog_id, message)
    await send_msg_info_to_dialog_participants(user, dialog_id, message)
