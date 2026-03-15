import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    pass


engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)
