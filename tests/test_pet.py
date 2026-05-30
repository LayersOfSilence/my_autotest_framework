import pytest
from models.petstore_models import Pet


@pytest.mark.smoke
def test_create_pet_minimal(api_client):
    """Создание питомца с минимальными полями"""
    pet_data = {
        "name": "TestDog",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": "available"
    }
    response = api_client.post("/pet", json=pet_data)
    assert response.status_code == 200
    pet = Pet(**response.json())
    assert pet.name == "TestDog"
    assert pet.status == "available"
    assert pet.id is not None
    # Очистка
    api_client.delete(f"/pet/{pet.id}")


@pytest.mark.smoke
def test_get_pet_by_id(api_client):
    """Получение питомца по ID"""
    # Создаём тестового питомца
    pet_data = {
        "name": "GetTestDog",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": "available"
    }
    create_resp = api_client.post("/pet", json=pet_data)
    pet_id = create_resp.json()["id"]
    # Получаем данные тестового питомца
    get_resp = api_client.get(f"/pet/{pet_id}")
    assert get_resp.status_code == 200
    pet = Pet(**get_resp.json())
    assert pet.id == pet_id
    assert pet.name == "GetTestDog"
    # Очистка
    api_client.delete(f"/pet/{pet_id}")


@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_create_pet_with_status(api_client, status):
    """Создание питомца с разными статусами"""
    pet_data = {
        "name": f"TestDog_{status}",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": status
    }
    response = api_client.post("/pet", json=pet_data)
    assert response.status_code == 200
    pet = Pet(**response.json())
    assert pet.status == status
    # Очистка
    api_client.delete(f"/pet/{pet.id}")


def test_get_pet_not_found(api_client):
    """Получение питомца с несуществующим ID → 404"""
    non_existent_id = 999999999
    response = api_client.get(f"/pet/{non_existent_id}")
    assert response.status_code == 404
    # В ответе ApiResponse модель
    from models.petstore_models import ApiResponse
    error = ApiResponse(**response.json())
    assert "not found" in error.message.lower()