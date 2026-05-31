import pytest
from models.petstore_models import Pet


@pytest.mark.smoke
@pytest.mark.parametrize("field_name, field_value", [
    ("name", "JustName"),
    ("photoUrls", ["https://example.com/only-photo.jpg"]),
    ("status", "available"),
    ("category", {"id": 1, "name": "Dogs"}),
    ("tags", [{"id": 1, "name": "friendly"}])
])
def test_create_pet_single_field(api_client, field_name, field_value):
    """Создание питомца с единственным полем"""
    pet_data = {field_name: field_value}
    response = api_client.post("/pet", json=pet_data)
    assert response.status_code == 200
    pet = Pet(**response.json())
    # Превращаем весь объект в словарь
    pet_dict = pet.model_dump()
    assert pet_dict.get(field_name) == field_value
    api_client.delete(f"/pet/{pet.id}")


@pytest.mark.smoke
def test_get_pet_by_id(api_client):
    """Получение питомца по ID"""
    pet_data = {
        "name": "GetTestDog",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": "available"
    }
    create_resp = api_client.post("/pet", json=pet_data)
    pet_id = create_resp.json()["id"]
    get_resp = api_client.get(f"/pet/{pet_id}")
    assert get_resp.status_code == 200
    pet = Pet(**get_resp.json())
    assert pet.id == pet_id
    assert pet.name == "GetTestDog"
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


def test_update_pet(api_client):
    """Проверяем обновление через PUT, PATCH petstore не поддерживает"""
    pet_data = {
        "name": "OriginalName",
        "photoUrls": ["https://example.com/photo1.jpg"],
        "status": "available"
    }
    create_resp = api_client.post("/pet", json=pet_data)
    pet_id = create_resp.json()["id"]
    update_data = {
        "id": pet_id,
        "name": "UpdatedName",
        "photoUrls": ["https://example.com/photo2.jpg"],  # изменили URL
        "status": "sold"
    }
    update_resp = api_client.put("/pet", json=update_data)
    assert update_resp.status_code == 200
    updated = Pet(**update_resp.json())
    assert updated.name == "UpdatedName"
    assert updated.photoUrls == ["https://example.com/photo2.jpg"]
    assert updated.status == "sold"
    api_client.delete(f"/pet/{pet_id}")
