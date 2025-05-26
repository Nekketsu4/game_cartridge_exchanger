import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import create_user_database, get_users, get_users_by_id

rdy_dict = {"name": "Kadyr", "surname": "Aziev", "email": "some@mail.ru"}


@pytest.mark.asyncio
async def test_get_user_by_id(async_client_test: AsyncClient):
    await create_user_database(**rdy_dict)  # создаем пользователя

    users = await get_users()  # список пользователей

    response = await async_client_test.get(f"/user/{users[0].user_id}")
    response_data = response.json()

    user_by_id = await get_users_by_id(users[0].user_id)

    assert response.status_code == 200
    assert len(response_data) > 0
    assert response_data["user_id"] == str(user_by_id.user_id)
    assert response_data["name"] == user_by_id.name
    assert response_data["surname"] == user_by_id.surname
    assert response_data["email"] == user_by_id.email
    assert response_data["is_active"] == user_by_id.is_active


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(async_client_test: AsyncClient):
    uncorrect_id = uuid.uuid4()
    response = await async_client_test.get(f"/user/{uncorrect_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "User was not found"}
