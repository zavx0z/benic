import json
import os
from pathlib import Path
from typing import List

import dramatiq
import dramatiq_abort
import socketio
import tailer
from dotenv import load_dotenv
from dramatiq.brokers.redis import RedisBroker
from dramatiq_abort import Abortable, backends
from pydantic import BaseModel

load_dotenv(Path(__file__).parents[1] / '.env')
REDIS_HOST = os.getenv('REDIS_HOST', "redis://0.0.0.0")
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

external_sio = socketio.RedisManager(f"{REDIS_HOST}:{REDIS_PORT}", write_only=True)

broker = RedisBroker(url=f"{REDIS_HOST}:{REDIS_PORT}/1")
broker.add_middleware(Abortable(backend=dramatiq_abort.backends.RedisBackend(client=broker.client)))
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


@dramatiq.actor(time_limit=float("inf"), max_retries=2)
def tail_logs(log_file_path):
    # connect to the redis queue as an external process
    # emit an event
    with open(log_file_path) as file:
        # читаем последние 100 строк из лог-файла
        last_lines = tailer.tail(file, 100)
        for line in last_lines:
            external_sio.emit('log', line)
    try:
        # запускаем чтение лог-файла в режиме tail
        for line in tailer.follow(open(log_file_path)):
            external_sio.emit('log', line)
    except Exception as e:
        print('Cancelled')
