import pytest
import requests
from config import BASE_URL
from models.petstore_models import Pet
from constants import PET_STATUSES, USER_STATUSES
from faker import Faker

fake = Faker()


# Fixtures
@pytest.fixture
def pet_data_full():
    """Полные данные питомца (со всеми полями)"""
    return {
        "name": f"FullPet_{int(fake.unix_time())}",
        "photoUrls": [fake.image_url(), fake.image_url()],
        "category": {
            "id": fake.random_int(min=1, max=100),
            "name": fake.word()
        },
        "tags": [
            {"id": fake.random_int(min=1, max=100), "name": fake.word()},
            {"id": fake.random_int(min=1, max=100), "name": fake.word()}
        ],
        "status": fake.random_element(PET_STATUSES)
    }


@pytest.fixture
def pet_data_minimal():
    """Минимальные данные питомца для создания в тестах."""
    return {
        "name": f"Pet_{fake.word()}_{int(fake.unix_time())}",
        "photoUrls": [fake.image_url()],
        "status": fake.random_element(PET_STATUSES)
    }


@pytest.fixture
def user_data():
    """Данные для создания пользователя"""
    username = fake.user_name()
    return {
        "username": username,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": f"{username}@example.com",
        "password": fake.password(length=10),
        "phone": fake.phone_number(),
        "userStatus": fake.random_element(USER_STATUSES)
    }


@pytest.fixture
def get_order_data():
    """Генерирует данные заказа для заданного питомца и статуса."""
    def _factory(pet_id, status="placed"):
        return {
            "petId": pet_id,
            "quantity": fake.random_int(min=1, max=5),
            "status": status,
            "complete": status == "delivered"
        }
    return _factory


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self.timeout = 10

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _request(self, method: str, endpoint: str, **kwargs):
        url = self._build_url(endpoint)
        return self.session.request(
            method,
            url,
            timeout=self.timeout,
            **kwargs
        )

    def post(self, endpoint: str, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def get(self, endpoint: str, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)


@pytest.fixture
def api_client() -> ApiClient:
    """Фикстура HTTP клиента."""
    return ApiClient(BASE_URL)


@pytest.fixture
def create_pet(api_client):
    """Фабрика для создания питомцев.
    Возвращает `create(pet_data) -> Pet`.
    Все созданные питомцы удаляются в teardown.
    """
    created = []

    def _create(pet_data: dict):
        resp = api_client.post("/pet", json=pet_data)
        assert resp.status_code == 200
        pet = Pet(**resp.json())
        created.append(pet.id)
        return pet

    yield _create

    for pid in created:
        try:
            api_client.delete(f"/pet/{pid}")
        except Exception:
            pass


@pytest.fixture
def create_user(api_client):
    """Фабрика для создания пользователей.
    Возвращает `create(user_data) -> Response`.
    Все созданные пользователи удаляются в teardown.
    """
    created = []

    def _create(user_data: dict):
        resp = api_client.post("/user", json=user_data)
        assert resp.status_code == 200
        created.append(user_data.get("username"))
        return resp

    yield _create

    for username in created:
        try:
            api_client.delete(f"/user/{username}")
        except Exception:
            pass


@pytest.fixture
def cleanup_users(api_client):
    """Вспомогательная фикстура для удаления пользователей.
    Используется для тестов, где нужно удалить несколько пользователей.
    Пример: cleanup_users.extend(['user1', 'user2'])
    """
    created = []
    yield created

    for username in created:
        try:
            if username:
                api_client.delete(f"/user/{username}")
        except Exception:
            pass


@pytest.fixture
def create_order(api_client):
    """Фабрика для создания заказов.
    Возвращает `create(order_data) -> order_id`.
    Если нужен временный питомец, создайте его с помощью `create_pet`.
    Передайте затем `petId`.
    Все созданные заказы удаляются в teardown.
    """
    created = []

    def _create(order_data: dict):
        resp = api_client.post("/store/order", json=order_data)
        assert resp.status_code == 200
        oid = resp.json().get("id")
        assert oid is not None
        created.append(oid)
        return oid

    yield _create

    for oid in created:
        try:
            if oid:
                url = f"/store/order/{oid}"
                api_client.delete(url)
        except Exception:
            pass
