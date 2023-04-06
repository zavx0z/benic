import logging
import sys
from datetime import datetime


class SIOFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        username, result = record.args
        action = f"{record.msg} {getattr(record, 'action', '')}"
        message = f"{action:20}{username:40} {result:40}{record.funcName:30}[{record.lineno:4}]{record.filename:20}{record.pathname}"
        return f"{timestamp} - {record.levelname:5} - {message}"


class ActionFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

        username, sid, action, channel, room = record.args
        message = f"|{record.msg:^6}|{username:^22}|{sid:^20}|{action.upper():^10}|{channel:^10}|{room:^20}|"

        call_position = f"{record.funcName}[{record.lineno:^4}]{record.pathname}"

        return f"{timestamp} - {record.levelname:5} - {message}{call_position}"


conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sio_formatter': {
            '()': SIOFormatter
        },
        'actionFormatter': {
            '()': ActionFormatter
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
        'actionConsole': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'actionFormatter'
        },
        'actionFile': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'actionFormatter'
        },
        "chat_handler": {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'chat_formatter'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'sio_formatter'
        }
    },
    'loggers': {
        'sio': {
            'level': 'DEBUG',
            'handlers': [
                'sio_handler',
                'file',
            ]
        },
        'action': {
            'level': 'DEBUG',
            'handlers': [
                'actionConsole',
                'actionFile',
            ]
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
