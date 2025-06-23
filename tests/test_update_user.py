import pytest
from httpx import AsyncClient

from database.models import RolesCredentions
from security.hashing import get_password_hash
from tests.conftest import create_testing_token, create_user_database, get_users

data_user = {
    "name": "Kadyr",
    "surname": "Aziev",
    "email": "some@mail.ru",
    "password": get_password_hash("password"),
    "roles": [
        RolesCredentions.ROLE_USER,
    ],
}


@pytest.mark.asyncio
async def test_update_user(async_client_test: AsyncClient):
    data_to_update = {"name": "Salmara", "surname": "Terso", "email": "livio@gmail.com"}

    user = await create_user_database(**data_user)  # создаем пользователя
    updated = await async_client_test.patch(
        f"/user/{user.user_id}",
        json=data_to_update,
        headers=create_testing_token(email=user.email),
    )
    updated_user = await get_users()

    # get_user = await async_client_test.get(
    #     f"/user/{user.user_id}",
    #     headers=create_testing_token(email=user.email)
    # )

    # проверяем попратченные данные
    assert updated.status_code == 200
    assert user.user_id == updated_user[0].user_id
    assert user.is_active == updated_user[0].is_active
    assert data_to_update["name"] == updated_user[0].name
    assert data_to_update["surname"] == updated_user[0].surname
    assert data_to_update["email"] == updated_user[0].email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status_code, expected_detail",
    [
        ({}, 422, {"detail": "Body is empty"}),
        (
            {"name": 123},
            422,
            {
                "detail": [
                    {
                        "type": "string_type",
                        "loc": ["body", "name"],
                        "msg": "Input should be a valid string",
                        "input": 123,
                    }
                ]
            },
        ),
    ],
)
async def test_update_user_incorrect_request(
    async_client_test: AsyncClient, update_data, expected_status_code, expected_detail
):
    user = await create_user_database(**data_user)
    updated_user = await async_client_test.patch(
        f"/user/{user.user_id}",
        json=update_data,
        headers=create_testing_token(email=user.email),
    )

    assert updated_user.status_code == expected_status_code
    assert updated_user.json()["detail"] == expected_detail["detail"]
