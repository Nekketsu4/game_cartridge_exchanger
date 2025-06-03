import pytest
from httpx import AsyncClient

from security.hashing import get_password_hash
from tests.conftest import create_testing_token, create_user_database

rdy_dict = {
    "name": "Kadyr",
    "surname": "Aziev",
    "email": "some@mail.ru",
    "password": get_password_hash("password"),
}


@pytest.mark.asyncio
async def test_delete_user(async_client_test: AsyncClient):
    """
    Тест на успешное удаление 200
    """
    user = await create_user_database(**rdy_dict)
    response = await async_client_test.delete(
        f"/user/{user.user_id}", headers=create_testing_token(user.email)
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": f"User with ID:{user.user_id} has been deleted"
    }


@pytest.mark.asyncio
async def test_delete_user_not_found(async_client_test: AsyncClient):
    """
    Тест на не верный ID пользователя 404
    """
    user = await create_user_database(**rdy_dict)
    response = await async_client_test.delete(
        f"/user/{'faaab5bc-9e27-4498-a71a-ee449126d91e'}",
        headers=create_testing_token(email=user.email),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User was not found"}


@pytest.mark.asyncio
async def test_delete_user_unauthorized(async_client_test: AsyncClient):
    """
    Тест на не верный токен
    """
    user = await create_user_database(**rdy_dict)
    user_token = user.email + "a"
    response = await async_client_test.delete(
        f"/user/{user.user_id}", headers=create_testing_token(email=user_token)
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "User unauthorized"}
