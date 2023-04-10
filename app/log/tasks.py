import dramatiq
import dramatiq_abort
import socketio
import tailer

from config import REDIS_HOST, REDIS_PORT

external_sio = socketio.RedisManager(f"{REDIS_HOST}:{REDIS_PORT}", write_only=True)


@dramatiq.actor(time_limit=float("inf"), max_retries=0)
def tail_logs(log_file_path):
    # connect to the redis queue as an external process
    # emit an event
    with open(log_file_path) as file:
        # читаем последние 100 строк из лог-файла
        last_lines = tailer.tail(file, 100)
        for line in last_lines:
            external_sio.emit('log', line)
    # запускаем чтение лог-файла в режиме tail
    with open(log_file_path) as file:
        for line in tailer.follow(file):
            if dramatiq_abort.abort_requested():
                print('Aborted tail_logs task')
                break  # прерываем операцию tail при запросе аборта
            external_sio.emit('log', line)
