import logging
import sys
from datetime import datetime


class MyFormatter(logging.Formatter):
    def format(self, record):
        room, username = record.args
        action_string = f"{record.msg.upper()}{getattr(record, 'action', '')}"
        message = f"{action_string:10}{room:20} from: {username}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        return f"{timestamp} - {record.levelname} - {record.name} - {message}"


conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sio_formatter': {
            '()': MyFormatter
        },
    },
    'handlers': {
        'sio_handler': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'sio_formatter'
        }
    },
    'loggers': {
        'sio': {
            'level': 'DEBUG',
            'handlers': ['sio_handler']
        }
    }
}
