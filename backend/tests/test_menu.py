import uuid


def test_add_menu_item(client, sample_restaurant):
    """Test adding a menu item to a restaurant."""
    payload = {
        "name": "Classic Cheeseburger",
        "description": "Beef patty, cheddar cheese, brioche bun",
        "price": "8.50",
        "category": "Burgers",
        "image_url": "https://example.com/burger.jpg",
        "is_available": True,
    }
    response = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu", json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Classic Cheeseburger"
    assert data["price"] == "8.50"
    assert data["restaurant_id"] == str(sample_restaurant.id)
    assert data["is_available"] is True


def test_reject_menu_item_invalid_restaurant(client):
    """Test adding item to a non-existent restaurant returns 404."""
    random_restaurant_id = uuid.uuid4()
    payload = {
        "name": "Ghost Dish",
        "price": "5.00",
        "category": "Mains",
    }
    response = client.post(
        f"/api/restaurants/{random_restaurant_id}/menu", json=payload
    )
    assert response.status_code == 404


def test_reject_menu_item_invalid_price(client, sample_restaurant):
    """Test that zero or negative prices are rejected by validation (422)."""
    # Negative price
    payload_negative = {
        "name": "Free Soda",
        "price": "-1.50",
        "category": "Drinks",
    }
    res1 = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu", json=payload_negative
    )
    assert res1.status_code == 422

    # Zero price
    payload_zero = {
        "name": "Zero Burger",
        "price": "0.00",
        "category": "Mains",
    }
    res2 = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu", json=payload_zero
    )
    assert res2.status_code == 422


def test_get_menu_and_filter(client, sample_restaurant):
    """Test getting restaurant menu with category and availability filters."""
    # Add two items
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Iced Tea", "price": "2.50", "category": "Beverages", "is_available": True},
    )
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Hot Chocolate", "price": "3.50", "category": "Beverages", "is_available": False},
    )
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "French Fries", "price": "4.00", "category": "Sides", "is_available": True},
    )

    # 1. Get all items
    res_all = client.get(f"/api/restaurants/{sample_restaurant.id}/menu")
    assert res_all.status_code == 200
    assert res_all.json()["total"] == 3

    # 2. Filter by category
    res_beverages = client.get(
        f"/api/restaurants/{sample_restaurant.id}/menu?category=Beverages"
    )
    assert res_beverages.status_code == 200
    assert res_beverages.json()["total"] == 2

    # 3. Filter by availability
    res_available = client.get(
        f"/api/restaurants/{sample_restaurant.id}/menu?is_available=true"
    )
    assert res_available.status_code == 200
    assert res_available.json()["total"] == 2


def test_get_update_and_delete_menu_item(client, sample_restaurant):
    """Test menu item details retrieval, update, availability toggle, and deletion."""
    create_res = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Chicken Wrap", "price": "7.00", "category": "Wraps"},
    )
    item_id = create_res.json()["id"]

    # 1. Get details
    get_res = client.get(f"/api/menu/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Chicken Wrap"

    # 2. Update item
    update_res = client.put(
        f"/api/menu/{item_id}",
        json={"price": "7.50", "name": "Spicy Chicken Wrap"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Spicy Chicken Wrap"
    assert update_res.json()["price"] == "7.50"

    # 3. Patch availability
    patch_res = client.patch(
        f"/api/menu/{item_id}/availability",
        json={"is_available": False},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["is_available"] is False

    # 4. Delete item
    delete_res = client.delete(f"/api/menu/{item_id}")
    assert delete_res.status_code == 200

    # 5. Verify deleted
    verify_res = client.get(f"/api/menu/{item_id}")
    assert verify_res.status_code == 404

