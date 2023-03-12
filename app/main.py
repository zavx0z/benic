from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic.main import BaseModel

from auth.routes import refresh, login, user, join
from chat import routes
from config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from shared.socketio import sio_app
import chat.socketio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(routes.router)

app.mount('/', sio_app)
