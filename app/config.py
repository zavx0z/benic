import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from logger import conf

load_dotenv(Path(__file__).parents[1] / '.env')
logging.config.dictConfig(conf)

POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

REDIS_HOST = f"redis://{os.getenv('REDIS_HOST', '0.0.0.0')}"
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
ASYNC_REDIS_MANAGER = f"{REDIS_HOST}:{REDIS_PORT}"

if os.getenv('DEVELOP'):
    POSTGRES_HOST = 'localhost'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'secret')
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 4
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

ADMIN_ID = 1
ADMIN_ORIGIN = [
    'http://localhost:3001',
    'https://admin-botswork.web.app'
]
