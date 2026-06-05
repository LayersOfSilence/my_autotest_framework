import pytest
from faker import Faker
from constants import NON_EXISTENT_USERNAME
from models.petstore_models import User, ApiResponse


fake = Faker()


@pytest.mark.smoke
def test_create_user(user_data, create_user):
    """Создание пользователя"""
    response = create_user(user_data)
    result = ApiResponse(**response.json())
    assert result.code == 200


@pytest.mark.smoke
def test_get_user_by_username(api_client, user_data, create_user):
    """Получение пользователя по имени"""
    create_user(user_data)
    username = user_data["username"]
    response = api_client.get(f"/user/{username}")
    assert response.status_code == 200
    user = User(**response.json())
    assert user.username == username
    assert user.firstName == user_data["firstName"]


def test_get_nonexistent_user(api_client):
    """Получение несуществующего пользователя"""
    response = api_client.get(f"/user/{NON_EXISTENT_USERNAME}")
    assert response.status_code == 404


@pytest.mark.skip(reason="petstore не возвращает изменения user после PUT")
def test_update_user(api_client, user_data, create_user):
    """Обновение пользователя"""
    username = user_data["username"]
    # Создаём и логинимся
    create_user(user_data)
    login_resp = api_client.get("/user/login",
                                params={"username": username,
                                        "password": user_data["password"]})
    assert login_resp.status_code == 200
    assert "logged in" in ApiResponse(**login_resp.json()).message.lower()
    # Обновляем
    new_data = {
        "username": username,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "phone": fake.phone_number(),
        "userStatus": 0
    }
    assert api_client.put(f"/user/{username}",
                          json=new_data).status_code == 200
    # Проверяем все поля
    user = User(**api_client.get(f"/user/{username}").json())
    for field in ["firstName", "lastName", "email", "password",
                  "phone", "userStatus"]:
        assert getattr(user, field) == new_data[field]
    api_client.delete(f"/user/{username}")


@pytest.mark.smoke
def test_delete_user(api_client, user_data, create_user):
    """Удаление пользователя"""
    username = user_data["username"]
    create_user(user_data)
    delete_resp = api_client.delete(f"/user/{username}")
    assert delete_resp.status_code == 200
    get_resp = api_client.get(f"/user/{username}")
    assert get_resp.status_code == 404


@pytest.mark.smoke
def test_user_login_logout(api_client, user_data, create_user):
    """Логин и логаут пользователя"""
    username = user_data["username"]
    password = user_data["password"]
    create_user(user_data)
    login_resp = api_client.get("/user/login", params={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    result = ApiResponse(**login_resp.json())
    assert "logged in" in result.message.lower()
    logout_resp = api_client.get("/user/logout")
    assert logout_resp.status_code == 200


def test_create_users_with_list(api_client, user_data, cleanup_users):
    """Создание нескольких пользователей списком"""
    second_user = user_data.copy()
    second_user["username"] = fake.user_name()
    second_user["email"] = f"{second_user['username']}@example.com"
    users = [user_data, second_user]
    response = api_client.post("/user/createWithList", json=users)
    if response.status_code == 200:
        cleanup_users.extend([user["username"] for user in users])
    assert response.status_code == 200
