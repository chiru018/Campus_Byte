import uuid
from decimal import Decimal
from app.models import Order, OrderItem, OrderStatus, PaymentStatus


def test_get_categories(client):
    """Test retrieving available standard food categories."""
    response = client.get("/api/menu/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 10
    keys = [c["key"] for c in categories]
    assert "BIRYANI" in keys
    assert "PIZZA" in keys
    assert "BURGERS" in keys
    assert "BEVERAGES" in keys


def test_add_menu_item(client, sample_restaurant, owner_headers):
    """Test adding a menu item to a restaurant by its legitimate owner."""
    payload = {
        "name": "Classic Cheeseburger",
        "description": "Beef patty, cheddar cheese, brioche bun",
        "price": "8.50",
        "category": "BURGERS",
        "image_url": "https://example.com/burger.jpg",
        "is_available": True,
    }
    response = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json=payload,
        headers=owner_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Classic Cheeseburger"
    assert data["price"] == "8.50"
    assert data["restaurant_id"] == str(sample_restaurant.id)
    assert data["is_available"] is True


def test_reject_add_menu_item_by_customer(client, sample_restaurant, customer_headers):
    """Test creating menu item by customer returns 403 Forbidden."""
    payload = {
        "name": "Student Special",
        "price": "3.00",
        "category": "FAST_FOOD",
    }
    response = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json=payload,
        headers=customer_headers,
    )
    assert response.status_code == 403


def test_reject_add_menu_item_by_other_owner_idor(client, sample_restaurant, other_owner_headers):
    """Test IDOR prevention: Owner B cannot add menu items to Owner A's restaurant (403 Forbidden)."""
    payload = {
        "name": "Hostile Takeover Dish",
        "price": "10.00",
        "category": "PIZZA",
    }
    response = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json=payload,
        headers=other_owner_headers,
    )
    assert response.status_code == 403


def test_reject_menu_item_invalid_restaurant(client, owner_headers):
    """Test adding item to a non-existent restaurant returns 404 Not Found."""
    random_restaurant_id = uuid.uuid4()
    payload = {
        "name": "Ghost Dish",
        "price": "5.00",
        "category": "OTHER",
    }
    response = client.post(
        f"/api/restaurants/{random_restaurant_id}/menu",
        json=payload,
        headers=owner_headers,
    )
    assert response.status_code == 404


def test_reject_menu_item_invalid_price(client, sample_restaurant, owner_headers):
    """Test that zero or negative prices are rejected by validation (422)."""
    # Negative price
    payload_negative = {
        "name": "Free Soda",
        "price": "-1.50",
        "category": "BEVERAGES",
    }
    res1 = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json=payload_negative,
        headers=owner_headers,
    )
    assert res1.status_code == 422

    # Zero price
    payload_zero = {
        "name": "Zero Burger",
        "price": "0.00",
        "category": "BURGERS",
    }
    res2 = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json=payload_zero,
        headers=owner_headers,
    )
    assert res2.status_code == 422


def test_reject_menu_item_invalid_category(client, sample_restaurant, owner_headers):
    """Test that unrecognized categories are rejected (422)."""
    payload_invalid = {
        "name": "Flying Carpet",
        "price": "12.00",
        "category": "TOTALLY_INVALID_CATEGORY_XYZ",
    }
    res = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json=payload_invalid,
        headers=owner_headers,
    )
    assert res.status_code == 422


def test_get_menu_and_filter(client, sample_restaurant, owner_headers):
    """Test getting restaurant menu with category, availability, and search filters."""
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Iced Tea", "price": "2.50", "category": "BEVERAGES", "is_available": True},
        headers=owner_headers,
    )
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Hot Chocolate", "price": "3.50", "category": "BEVERAGES", "is_available": False},
        headers=owner_headers,
    )
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "French Fries", "price": "4.00", "category": "FAST_FOOD", "is_available": True},
        headers=owner_headers,
    )

    # 1. Get all items
    res_all = client.get(f"/api/restaurants/{sample_restaurant.id}/menu")
    assert res_all.status_code == 200
    assert res_all.json()["total"] == 3

    # 2. Filter by category
    res_beverages = client.get(
        f"/api/restaurants/{sample_restaurant.id}/menu?category=BEVERAGES"
    )
    assert res_beverages.status_code == 200
    assert res_beverages.json()["total"] == 2

    # 3. Filter by availability
    res_available = client.get(
        f"/api/restaurants/{sample_restaurant.id}/menu?is_available=true"
    )
    assert res_available.status_code == 200
    assert res_available.json()["total"] == 2

    # 4. Search by keyword
    res_search = client.get(
        f"/api/restaurants/{sample_restaurant.id}/menu?search=Fries"
    )
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["name"] == "French Fries"


def test_get_update_and_delete_menu_item(client, sample_restaurant, owner_headers, other_owner_headers):
    """Test retrieving, updating, availability toggling, and deleting an item."""
    # 1. Create item
    res_create = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Veggie Roll", "price": "6.00", "category": "FAST_FOOD"},
        headers=owner_headers,
    )
    item_id = res_create.json()["id"]

    # 2. Get item details (public)
    res_get = client.get(f"/api/menu/{item_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Veggie Roll"

    # 3. Update by other owner -> 403 Forbidden (IDOR)
    res_idor = client.put(
        f"/api/menu/{item_id}",
        json={"name": "Hacked Name"},
        headers=other_owner_headers,
    )
    assert res_idor.status_code == 403

    # 4. Update by legitimate owner -> 200 OK
    res_update = client.put(
        f"/api/menu/{item_id}",
        json={"name": "Crispy Veggie Spring Roll", "price": "6.75"},
        headers=owner_headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Crispy Veggie Spring Roll"
    assert res_update.json()["price"] == "6.75"

    # 5. Patch availability
    res_avail = client.patch(
        f"/api/menu/{item_id}/availability",
        json={"is_available": False},
        headers=owner_headers,
    )
    assert res_avail.status_code == 200
    assert res_avail.json()["is_available"] is False

    # 6. Delete clean item
    res_del = client.delete(f"/api/menu/{item_id}", headers=owner_headers)
    assert res_del.status_code == 200
    assert res_del.json()["is_deactivated"] is False

    # Verify 404
    assert client.get(f"/api/menu/{item_id}").status_code == 404


def test_delete_menu_item_with_historical_orders_deactivates(client, sample_restaurant, sample_customer, owner_headers, db_session):
    """Test that menu items with historical orders are soft-deactivated (is_available=False) to preserve referential integrity."""
    # Create item
    res_create = client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Special Biryani", "price": "14.50", "category": "BIRYANI"},
        headers=owner_headers,
    )
    item_id = uuid.UUID(res_create.json()["id"])

    # Create dummy historical order referencing this item
    order = Order(
        customer_id=sample_customer.id,
        restaurant_id=sample_restaurant.id,
        delivery_address="Dormitory Block B, Rm 304",
        subtotal=Decimal("14.50"),
        delivery_fee=Decimal("2.00"),
        total_amount=Decimal("16.50"),
        order_status=OrderStatus.DELIVERED,
        payment_status=PaymentStatus.PAID,
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        menu_item_id=item_id,
        item_name="Special Biryani",
        unit_price=Decimal("14.50"),
        quantity=1,
        total_price=Decimal("14.50"),
    )
    db_session.add(order_item)
    db_session.commit()

    # Attempt delete
    res_del = client.delete(f"/api/menu/{item_id}", headers=owner_headers)
    assert res_del.status_code == 200
    data = res_del.json()
    assert data["is_deactivated"] is True
    assert "deactivated" in data["message"]

    # Verify item still exists in DB but is_available is False
    res_get = client.get(f"/api/menu/{item_id}")
    assert res_get.status_code == 200
    assert res_get.json()["is_available"] is False
