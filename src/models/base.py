import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.data.constants import DEFAULT_DB_URL


class Base(DeclarativeBase):
    pass


engine = create_async_engine(os.getenv("DATABASE_URL", DEFAULT_DB_URL), echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)
