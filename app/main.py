from dramatiq_abort import abort
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic.main import BaseModel

from app.routes import router as app_router
from auth.routes import refresh, login, user, join
from config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from server.routes import router as server_router
from shared.socketio.connect import sio_app, sio
import chat.socketio
import chat.channels.dialog
from task.routes import router as task_router
from worker import tail_logs, get_running_tasks
from workspace.routes import router as workspace_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

message_id = None  # Инициализация переменной фоновой задачи


@app.post("/api.v1/log/start")
def start_tail_logs():
    tasks = get_running_tasks()
    if not any(task.actor_name for task in tasks):
        tail_logs.send('app.log')


@app.post("/api.v1/log/stop")
def stop_tail_logs():
    tasks = get_running_tasks()
    task = next(filter(lambda v: v.actor_name == 'tail_logs', tasks), None)
    abort(message_id=task.message_id)


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
