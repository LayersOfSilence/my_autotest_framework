import pytest
from faker import Faker
from constants import NON_EXISTENT_ID, PET_STATUSES
from models.petstore_models import Pet, ApiResponse


fake = Faker()


@pytest.mark.smoke
def test_create_pet_full_data(pet_data_full, create_pet):
    """Создание питомца со всеми полями"""
    pet = create_pet(pet_data_full)
    assert pet.name == pet_data_full["name"]
    assert len(pet.photoUrls) == len(pet_data_full["photoUrls"])
    assert pet.category.name == pet_data_full["category"]["name"]
    assert pet.category.id == pet_data_full["category"]["id"]
    assert len(pet.tags) == len(pet_data_full["tags"])
    assert pet.tags[0].name == pet_data_full["tags"][0]["name"]
    assert pet.tags[1].name == pet_data_full["tags"][1]["name"]
    assert pet.status == pet_data_full["status"]
    assert pet.id is not None


@pytest.mark.parametrize("key, value", [
    ("name", "TestName"),
    ("photoUrls", ["https://example.com/test.jpg"]),
    ("status", "available"),
    ("category", {"id": 1, "name": "Dogs"}),
    ("tags", [{"id": 1, "name": "friendly"}])
])
def test_create_pet_single_field(key, value, create_pet):
    """Создание питомца с единственным полем"""
    pet_data = {key: value}
    pet = create_pet(pet_data)
    # Превращаем весь объект в словарь
    pet_dict = pet.model_dump()
    assert pet_dict.get(key) == value


@pytest.mark.parametrize("status", PET_STATUSES)
def test_create_pet_with_status(status, create_pet):
    """Создание питомца с разными статусами"""
    pet_data = {
        "name": f"TestDog_{status}_{fake.word()}",
        "photoUrls": [fake.image_url()],
        "status": status
    }
    pet = create_pet(pet_data)
    assert pet.status == status


@pytest.mark.smoke
def test_get_pet_by_id(api_client, create_pet, pet_data_minimal):
    """Получение питомца по ID"""
    pet = create_pet(pet_data_minimal)
    pet_id = pet.id
    get_resp = api_client.get(f"/pet/{pet_id}")
    assert get_resp.status_code == 200
    pet2 = Pet(**get_resp.json())
    assert pet2.id == pet_id
    assert pet2.name == pet.name


def test_get_nonexistent_pet(api_client):
    """Получение питомца с несуществующим ID → 404"""
    response = api_client.get(f"/pet/{NON_EXISTENT_ID}")
    assert response.status_code == 404
    error = ApiResponse(**response.json())
    assert "not found" in error.message.lower()


@pytest.mark.smoke
def test_update_pet(api_client, create_pet, pet_data_minimal):
    """Проверяем обновление через PUT, PATCH petstore не поддерживает"""
    pet = create_pet(pet_data_minimal)
    pet_id = pet.id
    update_data = {
        "id": pet_id,
        "name": f"Updated_{fake.word()}",
        "photoUrls": [fake.image_url()],
        "status": "sold"
    }
    update_resp = api_client.put("/pet", json=update_data)
    assert update_resp.status_code == 200
    updated = Pet(**update_resp.json())
    assert updated.name == update_data["name"]
    assert updated.photoUrls == update_data["photoUrls"]
    assert updated.status == "sold"
    # cleanup performed by create_pet fixture


@pytest.mark.skip(reason="petstore всегда возвращает 200 на попытку обновить "
                  "несуществующего питомца, а должен 404")
def test_update_nonexistent_pet(api_client):
    """Обновление несуществующего питомца"""
    update_data = {
        "id": NON_EXISTENT_ID,
        "name": "GhostDog",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": "available"
    }
    response = api_client.put("/pet", json=update_data)
    assert response.status_code == 404
    from models.petstore_models import ApiResponse
    error = ApiResponse(**response.json())
    assert "not found" in error.message.lower()


@pytest.mark.smoke
def test_delete_pet(api_client, create_pet, pet_data_minimal):
    """Удаление питомца"""
    pet = create_pet(pet_data_minimal)
    pet_id = pet.id
    delete_resp = api_client.delete(f"/pet/{pet_id}")
    assert delete_resp.status_code == 200
    get_resp = api_client.get(f"/pet/{pet_id}")
    assert get_resp.status_code == 404


@pytest.mark.skip(reason="petstore ничего не возвращает на попытку удалить "
                  "несуществующего питомца, а должен 404")
def test_delete_nonexistent_pet(api_client):
    """Удаление питомца с несуществующим ID → 404"""
    response = api_client.delete(f"/pet/{NON_EXISTENT_ID}")
    assert response.status_code == 404
    from models.petstore_models import ApiResponse
    error = ApiResponse(**response.json())
    assert "not found" in error.message.lower()
