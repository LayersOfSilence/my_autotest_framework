import pytest
from faker import Faker
from models.petstore_models import User, ApiResponse


fake = Faker()


def get_user_data():
    """Генератор данных пользователя"""
    username = fake.user_name()
    return {
        "username": username,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": f"{username}@example.com",
        "password": fake.password(length=10),
        "phone": fake.phone_number(),
        "userStatus": 1
    }


@pytest.mark.smoke
def test_create_user(api_client):
    """Создание пользователя"""
    user_data = get_user_data()
    username = user_data["username"]
    response = api_client.post("/user", json=user_data)
    assert response.status_code == 200
    result = ApiResponse(**response.json())
    assert result.code == 200
    api_client.delete(f"/user/{username}")


@pytest.mark.smoke
def test_get_user_by_username(api_client):
    """Получение пользователя по имени"""
    user_data = get_user_data()
    username = user_data["username"]
    api_client.post("/user", json=user_data)
    response = api_client.get(f"/user/{username}")
    assert response.status_code == 200
    user = User(**response.json())
    assert user.username == username
    assert user.firstName == user_data["firstName"]
    api_client.delete(f"/user/{username}")


def test_get_user_not_found(api_client):
    """Получение несуществующего пользователя"""
    response = api_client.get(f"/user/{fake.user_name()}")
    assert response.status_code == 404


@pytest.mark.skip(reason="petstore не возврвщает изменения user после PUT")
def test_update_user(api_client):
    """Обновление пользователя"""
    user_data = get_user_data()
    username = user_data["username"]
    api_client.post("/user", json=user_data)
    login_resp = api_client.get("/user/login", params={
        "username": username,
        "password": user_data["password"]
    })
    assert login_resp.status_code == 200
    login_result = ApiResponse(**login_resp.json())
    assert "logged in" in login_result.message.lower()
    new_first_name = fake.first_name()
    new_last_name = fake.last_name()
    new_email = fake.email()
    new_password = fake.password()
    new_phone = fake.phone_number()
    update_data = {
        "username": username,
        "firstName": new_first_name,
        "lastName": new_last_name,
        "email": new_email,
        "password": new_password,
        "phone": new_phone,
        "userStatus": 0
    }
    response = api_client.put(f"/user/{username}", json=update_data)
    assert response.status_code == 200
    get_resp = api_client.get(f"/user/{username}")
    user = User(**get_resp.json())
    assert user.firstName == new_first_name
    assert user.lastName == new_last_name
    assert user.email == new_email
    assert user.password == new_password
    assert user.phone == new_phone
    assert user.userStatus == 0
    api_client.delete(f"/user/{username}")


@pytest.mark.smoke
def test_delete_user(api_client):
    """Удаление пользователя"""
    user_data = get_user_data()
    username = user_data["username"]
    api_client.post("/user", json=user_data)
    delete_resp = api_client.delete(f"/user/{username}")
    assert delete_resp.status_code == 200
    get_resp = api_client.get(f"/user/{username}")
    assert get_resp.status_code == 404


@pytest.mark.smoke
def test_user_login_logout(api_client):
    """Логин и логаут пользователя"""
    user_data = get_user_data()
    username = user_data["username"]
    password = user_data["password"]
    api_client.post("/user", json=user_data)
    login_resp = api_client.get("/user/login", params={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    result = ApiResponse(**login_resp.json())
    assert "logged in" in result.message.lower()
    logout_resp = api_client.get("/user/logout")
    assert logout_resp.status_code == 200
    api_client.delete(f"/user/{username}")


def test_create_users_with_list(api_client):
    """Создание нескольких пользователей списком"""
    users = [get_user_data() for _ in range(2)]
    response = api_client.post("/user/createWithList", json=users)
    assert response.status_code == 200
    for user in users:
        api_client.delete(f"/user/{user['username']}")
