import pytest

from httpx import AsyncClient
from tests.conftest import get_users_by_id, create_user_database

rdy_dict = {
         'name': 'Kadyr',
         'surname': 'Aziev',
         'email': 'some@mail.ru'
        }

rdy_dict2 = {
         'name': 'Kerim',
         'surname': 'Kurpanov',
         'email': 'kurp@mail.ru'
        }

@pytest.mark.asyncio
async def test_get_person(async_client_test: AsyncClient):
        """
        Test post endpoint that returns expected data

        execute post request with the data and then сompare saved DB data with
        json data received during the post request
        """
        await create_user_database(**rdy_dict2) # create user

        response = await async_client_test.post("/user/", json=rdy_dict)
        resp_data = response.json()

        res = await get_users_by_id(resp_data['user_id']) # get created user from DB

        assert response.status_code == 200
        assert resp_data['user_id'] == str(res.user_id)
        assert resp_data['name'] == res.name
        assert resp_data['surname'] == res.surname
        assert resp_data['email'] == res.email
        assert resp_data['is_active'] == res.is_active
        response2 = await async_client_test.post("/user/", json=rdy_dict) #проверка на ошибку вызванная существующим пользователем
        assert response2.status_code == 500
        assert 'User already exists' == response2   .json()['detail']


@pytest.mark.asyncio
@pytest.mark.parametrize("expected_user_data, expected_status_code, expected_detail", [ #кейс когда тело запроса пустое
    ({}, 422, {"detail": [{"type": "missing","loc": ["body","name"], "msg": "Field required","input": {}},
                          {"type": "missing","loc": ["body","surname"], "msg": "Field required","input": {}},
                          {"type": "missing","loc": ["body","email"], "msg": "Field required","input": {}}]}),

    ({"name": 666, "surname": "Kelemski", "email": "example@mail.com"}, 422 , {"detail": [ # кейс когда имя не строковый тип
                        {"type": "string_type", "loc": ["body","name"],
                         "msg": "Input should be a valid string",
                         "input": 666}]}),

    ({"name": "Robert", "surname": 190, "email": "example@mail.com"}, 422, {"detail": [ # кейс когда фамилия не строковый тип
                        {"type": "string_type", "loc": ["body", "surname"],
                         "msg": "Input should be a valid string",
                         "input": 190}]}),

    ({"name": "Robert", "surname": "Kelemski", "email": "example.com"}, 422, {"detail": [ # кейс когда на корректность названия почты
    {"type": "value_error", "loc": ["body", "email"],
      "msg": "value is not a valid email address: An email address must have an @-sign.",
      "input": "example.com",
      "ctx": {"reason": "An email address must have an @-sign."}}]}),

    ({"name": "Robert6", "surname": "Kelemski", "email": "example@mail.com"}, 422 , {"detail": #кейс на проверку цифры в строке в поле name
                                                                               "Имя должно содержать буквы"}),

    ({"name": "Robert", "surname": "Kelem3ki", "email": "example@mail.com"}, 422, {"detail": #кейс на проверку цифры в строке в поле surname
                                                                            "Фамилия должна содержать буквы"})

])
async def test_get_person_validation_error(async_client_test, expected_user_data, expected_status_code, expected_detail):
    response = await async_client_test.post("/user/", json=expected_user_data)
    response_data = response.json()

    assert response.status_code == expected_status_code
    assert response_data == expected_detail