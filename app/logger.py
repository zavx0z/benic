import logging
import sys
from datetime import datetime


class MyFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        username, result = record.args
        action = f"{record.msg} {getattr(record, 'action', '')}"
        message = f"{action:20}{username:30} {result:30}{record.funcName:20}[{record.lineno:4}]{record.filename:20}{record.pathname}"
        msg = f"{timestamp} - {record.levelname} - {message}"
        return msg


conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sio_formatter': {
            '()': MyFormatter
        },
        'chat_formatter': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{'
        }
    },
    'handlers': {
        'sio_handler': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'sio_formatter'
        },
        "chat_handler": {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'chat_formatter'
        }
    },
    'loggers': {
        'sio': {
            'level': 'DEBUG',
            'handlers': ['sio_handler']
        },
        'chat': {
            'level': 'DEBUG',
            'handlers': ['chat_handler']
        }
    }
}

# Настраиваем логгер Socket.IO
socketio_logger = logging.getLogger('socketio')
socketio_logger.setLevel(logging.DEBUG)
# Создаем обработчик логов для вывода сообщений в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
socketio_logger.addHandler(console_handler)