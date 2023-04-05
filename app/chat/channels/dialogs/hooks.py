from chat.actions.user_create import create_support_dialog_and_send_welcome_message
from shared.socketio.connect import sio


async def after_create_user(user_id: int):
    """Инициализация вновь созданного пользователя """
    welcome_text = """Добро пожаловать в наш чат поддержки! 
Если у вас есть вопросы, задавайте их здесь.
Благодарим вас за выбор нашей платформы.
Если у вас есть отзывы или предложения, мы будем рады их услышать. """
    await create_support_dialog_and_send_welcome_message(sio, user_id=user_id, welcome_text=welcome_text)
