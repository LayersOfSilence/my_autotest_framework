import pytest
from faker import Faker
from constants import NON_EXISTENT_ID
from models.petstore_models import Order, ApiResponse

fake = Faker()


@pytest.mark.smoke
def test_create_order(
    api_client,
    create_pet,
    create_order,
    get_order_data,
    pet_data_minimal,
):
    """Создание заказа"""
    pet = create_pet({
        **pet_data_minimal,
        "name": f"OrderPet_{fake.word()}"
    })
    order_data = get_order_data(pet.id)
    order_id = create_order(order_data)
    get_resp = api_client.get(f"/store/order/{order_id}")
    assert get_resp.status_code == 200
    order = Order(**get_resp.json())
    assert order.petId == pet.id
    assert order.quantity == order_data["quantity"]
    assert order.status == "placed"
    assert order.id == order_id


def test_get_order_by_id(
    api_client,
    create_pet,
    create_order,
    get_order_data,
    pet_data_minimal,
):
    """Получение заказа по ID"""
    pet = create_pet({
        **pet_data_minimal,
        "name": f"GetOrderPet_{fake.word()}"
    })
    order_data = get_order_data(pet.id)
    order_id = create_order(order_data)
    get_resp = api_client.get(f"/store/order/{order_id}")
    assert get_resp.status_code == 200
    order = Order(**get_resp.json())
    assert order.id == order_id
    assert order.petId == pet.id


def test_delete_order(
    api_client,
    create_pet,
    create_order,
    get_order_data,
    pet_data_minimal,
):
    """Удаление заказа"""
    pet = create_pet({
        **pet_data_minimal,
        "name": f"DeleteOrderPet_{fake.word()}"
    })
    order_data = get_order_data(pet.id)
    order_id = create_order(order_data)
    delete_resp = api_client.delete(f"/store/order/{order_id}")
    assert delete_resp.status_code == 200
    get_resp = api_client.get(f"/store/order/{order_id}")
    assert get_resp.status_code == 404


@pytest.mark.parametrize("status", ["placed", "approved", "delivered"])
def test_create_order_with_status(
    api_client,
    status,
    create_pet,
    create_order,
    get_order_data,
    pet_data_minimal,
):
    """Создание заказа с разными статусами"""
    pet = create_pet({
        **pet_data_minimal,
        "name": f"StatusOrderPet_{status}_{fake.word()}"
    })
    order_data = get_order_data(pet.id, status)
    order_id = create_order(order_data)
    order = Order(**api_client.get(f"/store/order/{order_id}").json())
    assert order.status == status


def test_get_order_not_found(api_client):
    """Получение несуществующего заказа"""
    response = api_client.get(f"/store/order/{NON_EXISTENT_ID}")
    assert response.status_code == 404
    error = ApiResponse(**response.json())
    assert "not found" in error.message.lower()


def test_delete_order_not_found(api_client):
    """Удаление несуществующего заказа"""
    response = api_client.delete(f"/store/order/{NON_EXISTENT_ID}")
    assert response.status_code == 404


def test_get_inventory(api_client):
    """Получение инвентаря магазина"""
    response = api_client.get("/store/inventory")
    assert response.status_code == 200
    inventory = response.json()
    assert isinstance(inventory, dict)
    for status, count in inventory.items():
        assert isinstance(count, int)
        assert count >= 0


def test_create_order_invalid_pet_id(api_client, get_order_data):
    """Создание заказа с несуществующим petId"""
    order_data = get_order_data(NON_EXISTENT_ID)
    response = api_client.post("/store/order", json=order_data)
    if response.status_code == 200:
        order = Order(**response.json())
        api_client.delete(f"/store/order/{order.id}")
        print(f"⚠️ API allowed order with invalid petId: {order.id}")
    else:
        assert response.status_code in [400, 404]
