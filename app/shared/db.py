import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session


async def get_async_session():
    async with async_session() as session:
        yield session


def _read_sql(con, stmt):
    return pd.read_sql(stmt, con)


async def get_df(stmt, index=None):
    async with engine.begin() as conn:
        data = await conn.run_sync(_read_sql, stmt,)
    return data
