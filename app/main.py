import tailer
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic.main import BaseModel
from starlette.background import BackgroundTasks

from app.routes import router as app_router
from auth.routes import refresh, login, user, join
from config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from server.routes import router as server_router
from shared.socketio.connect import sio_app, sio
import chat.socketio
import chat.channels.dialog
from task.routes import router as task_router
from workspace.routes import router as workspace_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def tail_logs(log_file_path):
    with open(log_file_path) as file:
        # читаем последние 100 строк из лог-файла
        last_lines = tailer.tail(file, 100)
        for line in last_lines:
            await sio.emit("log", line)

    # запускаем чтение лог-файла в режиме tail
    for line in tailer.follow(open(log_file_path)):
        await sio.emit("log", line)


background_task = None  # Инициализация переменной фоновой задачи


@app.post("/api.v1/start_tail_logs")
def start_tail_logs(background_tasks: BackgroundTasks):
    global background_task  # Объявление глобальной переменной фоновой задачи
    # Проверка, что фоновая задача еще не запущена
    if background_task is None:
        # Запуск функции tail_logs() в фоновом режиме
        background_task = background_tasks.add_task(tail_logs, 'app.log')
    else:
        # Остановка фоновой задачи
        background_task.cancel()
        background_task = None


class Settings(BaseModel):
    """Settings management"""
    authjwt_secret_key: str = JWT_SECRET_KEY
    authjwt_access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES


@AuthJWT.load_config
def get_config():
    """Callback to get your configuration"""
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    """Callback to exception handler for authjwt in production, you can tweak performance using orjson response """
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(login.router)
app.include_router(join.router)
app.include_router(user.router)
app.include_router(refresh.router)
app.include_router(app_router)
app.include_router(server_router)
app.include_router(workspace_router)
app.include_router(task_router)

app.mount('/', sio_app)
