""""

>>> async def handler1(*args, **kwargs):
>>>     print(f"Handler 1 received event with args {args} and kwargs {kwargs}")
>>>
>>> async def handler2(*args, **kwargs):
>>>     print(f"Handler 2 received event with args {args} and kwargs {kwargs}")

>>> event_manager = AsyncEventManager()

Подписываемся на событие "event_type1" с двумя обработчиками

>>> event_manager.subscribe("event_type1", handler1)
>>> event_manager.subscribe("event_type1", handler2)

Оповещаем обработчиков о событии "event_type1" с передачей аргументов

>>> await event_manager.notify("event_type1", arg1=1, arg2=2)

Отписываемся от обработчика handler1

>>> event_manager.unsubscribe("event_type1", handler1)

повещаем обработчиков о событии "event_type1" с передачей аргументов

>>> await event_manager.notify("event_type1", arg1=3, arg2=4)
"""
from collections import defaultdict

AFTER_CREATE_USER = 'AFTER_CREATE_USER'
SIO_DISCONNECT = 'SIO_DISCONNECT'
SIO_CONNECT = 'SIO_CONNECT'


class AsyncEventManager:
    """ Класс для асинхронного управления событиями.

    attribute:
        handlers (defaultdict): Список обработчиков для каждого типа события.
    methods:
        subscribe(event_type, handler): Подписаться на определенный тип события.
        unsubscribe(event_type, handler): Отписаться от определенного типа события.
        notify(event_type, *args, **kwargs): Оповестить обработчиков о произошедшем событии.
    """

    def __init__(self):
        # Используем defaultdict, чтобы создать пустой список для нового типа события
        self.handlers = defaultdict(list)

    def subscribe(self, event_type, handler):
        # Добавляем обработчик для определенного типа события
        self.handlers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        # Удаляем обработчик для определенного типа события, если он есть
        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)

    async def notify(self, event_type, *args, **kwargs):
        # Оповещаем обработчиков о событии, передавая им переданные аргументы и ключевые аргументы
        for handler in self.handlers[event_type]:
            await handler(*args, **kwargs)


async_event_manager = AsyncEventManager()
