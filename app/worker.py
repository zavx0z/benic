import json
import os
from pathlib import Path
from typing import List

import dramatiq
import dramatiq_abort
from dotenv import load_dotenv
from dramatiq.brokers.redis import RedisBroker
from dramatiq_abort import Abortable, backends
from pydantic import BaseModel

load_dotenv(Path(__file__).parents[1] / '.env')
REDIS_HOST = f"redis://{os.getenv('REDIS_HOST', '0.0.0.0')}"
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
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
