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