import pytest

from httpx import AsyncClient
from tests.conftest import create_user_database, get_users


@pytest.mark.asyncio
async def test_update_user(async_client_test: AsyncClient):
    data_user = {
        'name': 'Kadyr',
        'surname': 'Aziev',
        'email': 'some@mail.ru'
    }

    data_to_update = {
        "name": "Salmara",
        "surname": "Terso",
        "email": "livio@gmail.com"
    }

    user = await create_user_database(**data_user)  # создаем пользователя
    await async_client_test.patch(f"/user/{user.user_id}", json=data_to_update)
    get_user = await async_client_test.get(f"/user/{user.user_id}")
    updated_user = get_user.json()

    # проверяем попратченные данные
    assert get_user.status_code == 200
    assert str(user.user_id) == updated_user['user_id']
    assert user.is_active == updated_user['is_active']
    assert data_to_update['name'] == updated_user['name']
    assert data_to_update['surname'] == updated_user['surname']
    assert data_to_update['email'] == updated_user['email']



@pytest.mark.asyncio
@pytest.mark.parametrize("update_data, expected_status_code, expected_detail", [
    ({}, 422, {"detail": "Body is empty"}),
    ({"name": 123}, 422, {""
                          "detail": [
        {'type': 'string_type',
         'loc': ['body', 'name'],
         'msg': 'Input should be a valid string',
         'input': 123}]})
])
async def test_update_user_uncorrect_request(async_client_test: AsyncClient,
                                             update_data,
                                             expected_status_code,
                                             expected_detail):

    user = await get_users()
    updated_user = await async_client_test.patch(f"/user/{user[0].user_id}", json=update_data)

    assert updated_user.status_code == expected_status_code
    assert updated_user.json()['detail'] == expected_detail['detail']