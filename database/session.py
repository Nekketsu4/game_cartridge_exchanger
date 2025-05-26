import config

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# CONNECT TO DATABASE

engine = create_async_engine(config.DATABASE_URL, echo=True)


async_session = async_sessionmaker(bind=engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

