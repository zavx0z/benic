from chat.channels import CHANNEL_SUPPORT
from chat.crud.dialog import create_dialog
from chat.crud.message import create_message
from config import ADMIN_ID

welcome_text = f"""Добро пожаловать в чат поддержки! 
Готовы ответить на любые Ваши вопросы.
Также в чате можно оставить ваш отзыв или предложения.
Благодарим Вас за выбор нашей платформы."""


async def after_create_user(user_id: int):
    """Инициализация вновь созданного пользователя

    - Создает диалог между пользователем и администратором. (диалог поддержки)
    - Создает приветственное сообщение. (от User.id == 1 (zavx0z) в диалог поддержки)
     """
    dialog = await create_dialog(CHANNEL_SUPPORT, user_id, [user_id, ADMIN_ID])
    message = await create_message(
        sender_id=1,
        dialog_id=dialog.id,
        text=welcome_text,
    )
