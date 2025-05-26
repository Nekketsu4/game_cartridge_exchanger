import pytest

from httpx import AsyncClient
from tests.conftest import create_user_database, get_users, get_users_by_id

rdy_dict = {
         'name': 'Kadyr',
         'surname': 'Aziev',
         'email': 'some@mail.ru'
        }

@pytest.mark.asyncio
async def test_delete_user(async_client_test: AsyncClient):

    await create_user_database(**rdy_dict)  # создаем пользователя

    users_before = await get_users()
    await async_client_test.delete(f"/user/{users_before[0].user_id}")
    users_after = await get_users()

    assert users_before != users_after


@pytest.mark.asyncio
async def test_delete_user_not_found(async_client_test: AsyncClient):

    response = await async_client_test.delete(f"/user/{'214c2128-5a9f-4c2d-8ed9-7a999d53b39c'}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User was not found"}