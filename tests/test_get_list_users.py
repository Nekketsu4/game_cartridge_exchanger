import pytest
from httpx import AsyncClient

from database.models import RolesCredentions
from security.hashing import get_password_hash
from tests.conftest import create_testing_token, create_user_database, get_users

rdy_dict = {
    "name": "Kadyr",
    "surname": "Aziev",
    "email": "some@mail.ru",
    "password": get_password_hash("password"),
    "roles": [
        RolesCredentions.ROLE_USER,
    ],
}


@pytest.mark.asyncio
async def test_get_users(async_client_test: AsyncClient):
    user = await create_user_database(**rdy_dict)  # create user

    response = await async_client_test.get(
        "/user/", headers=create_testing_token(email=user.email)
    )
    resp_data = response.json()

    users = await get_users()  # get created user from DB

    assert response.status_code == 200
    assert len(users) == len(resp_data)
    assert type(users) is list
