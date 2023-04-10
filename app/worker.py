import json
import logging
import logging.config as logger_conf
from typing import List

import dramatiq
import dramatiq_abort
import firebase_admin
import socketio
from dramatiq.brokers.redis import RedisBroker
from dramatiq_abort import Abortable, backends
from firebase_admin import credentials
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, REDIS_HOST, REDIS_PORT

conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s %(name)s:%(lineno)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'notifications.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'formatter': 'default',
        }
    },
    'loggers': {
        'dramatiq': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'notification': {
            'level': 'INFO',
            'handlers': ['file']
        }
    }
}
logger_conf.dictConfig(conf)

broker = RedisBroker(url=f"{REDIS_HOST}:{REDIS_PORT}/1")
broker.add_middleware(Abortable(backend=dramatiq_abort.backends.RedisBackend(client=broker.client)))
# broker.add_middleware(Results(backend=RedisBackend(url=f"{REDIS_HOST}:{REDIS_PORT}/2")))
dramatiq.set_broker(broker)


class TaskInfo(BaseModel):
    message_id: str
    actor_name: str
    queue_name: str
    message_timestamp: int


def get_running_tasks() -> List[TaskInfo]:
    task_ids = broker.client.hgetall("dramatiq:default.msgs")
    tasks_info = []
    for key, value in task_ids.items():
        key = key.decode()
        value = value.decode() if type(value) == bytes else value
        value = json.loads(value)
        task_info_obj = TaskInfo(**value)
        tasks_info.append(task_info_obj)
    return tasks_info


# SocketIO
sio_dramatiq = socketio.RedisManager(f"{REDIS_HOST}:{REDIS_PORT}", write_only=True)

# DataBase
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Notifications
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
