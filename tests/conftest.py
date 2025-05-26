import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import select
from pydantic import EmailStr




from httpx import AsyncClient, ASGITransport

import config
from main import app
from database.session import get_async_session
from database.models import Base, User

engine_test = create_async_engine(config.TEST_DATABASE_URL, poolclass=NullPool)
async_session_test = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, class_=AsyncSession
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="module")
async def prepare_database_test():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def async_client_test() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

async def create_user_database(name: str, surname: str, email: EmailStr):
    async with async_session_test() as session:
        user = User(name=name, surname=surname, email=email)
        session.add(user)
        await session.commit()
        return user

async def get_users():
    async with async_session_test() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users

async def get_users_by_id(user_id):
    async with async_session_test() as session:
        result = await session.execute(select(User).filter_by(user_id=user_id))
        user = result.scalar_one_or_none()
        return user


# def connection(method):
#     """
#     Создаем декоратор который создает сессию, асинхронного тестового клиента
#      и передает ее в функцию.
#     В случае неудачной транзакции, делаем откат
#     """
#     async def wrapper(async_client_test, *args, **kwargs):
#         async with async_session_test() as session:
#             try:
#                 return await method(async_client_test, *args, session=session, **kwargs)
#             except Exception as e:
#                 await session.rollback()
#                 raise e
#             finally:
#                 await session.close()
#
#     return wrapper


