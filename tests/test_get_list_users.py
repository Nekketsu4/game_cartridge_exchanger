import pytest
from httpx import AsyncClient

from tests.conftest import create_user_database, get_users

rdy_dict = {"name": "Kadyr", "surname": "Aziev", "email": "some@mail.ru"}


@pytest.mark.asyncio
async def test_get_users(async_client_test: AsyncClient):
    await create_user_database(**rdy_dict)  # create user

    response = await async_client_test.get("/user/")
    resp_data = response.json()

    users = await get_users()  # get created user from DB

    assert response.status_code == 200
    assert len(users) == len(resp_data)
    assert type(users) is list
