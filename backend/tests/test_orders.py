import uuid
from decimal import Decimal
import pytest
from app.models import MenuItem, Restaurant, Order
from app.models.enums import FoodCategory, OrderStatus, PaymentMethod, PaymentStatus


@pytest.fixture
def burger_item(db_session, sample_restaurant) -> MenuItem:
    """Sample burger item belonging to sample_restaurant."""
    item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=sample_restaurant.id,
        name="Double Cheeseburger",
        description="Juicy double beef patty with melted cheddar",
        price=Decimal("8.50"),
        category=FoodCategory.BURGERS,
        is_available=True,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def fries_item(db_session, sample_restaurant) -> MenuItem:
    """Sample fries item belonging to sample_restaurant."""
    item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=sample_restaurant.id,
        name="Crispy French Fries",
        description="Golden salted fries",
        price=Decimal("3.50"),
        category=FoodCategory.BEVERAGES,
        is_available=True,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def other_restaurant(db_session, other_owner) -> Restaurant:
    """A secondary restaurant."""
    rest = Restaurant(
        id=uuid.uuid4(),
        owner_id=other_owner.id,
        name="Luigi's Italian Pizza",
        address="Dormitory Block C",
        contact_number="+1555999888",
        is_open=True,
    )
    db_session.add(rest)
    db_session.commit()
    db_session.refresh(rest)
    return rest


@pytest.fixture
def pizza_item(db_session, other_restaurant) -> MenuItem:
    """Sample item belonging to other_restaurant."""
    item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=other_restaurant.id,
        name="Margherita Pizza",
        price=Decimal("12.00"),
        category=FoodCategory.PIZZA,
        is_available=True,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


# ==============================================================================
# ORDER CREATION TESTS
# ==============================================================================

def test_place_order_success(client, customer_headers, sample_restaurant, burger_item, fries_item):
    """Customer places order successfully with automatic server pricing."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel B, Room 304, Campus North",
        "payment_method": "CASH_ON_DELIVERY",
        "items": [
            {"menu_item_id": str(burger_item.id), "quantity": 2},
            {"menu_item_id": str(fries_item.id), "quantity": 1},
        ],
        "idempotency_key": "test-key-12345",
    }
    response = client.post("/api/orders", json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.json()

    # 2 x 8.50 = 17.00; 1 x 3.50 = 3.50; subtotal = 20.50; delivery_fee = 2.00; total = 22.50
    assert float(data["subtotal"]) == 20.50
    assert float(data["delivery_fee"]) == 2.00
    assert float(data["total_amount"]) == 22.50
    assert data["order_status"] == "PENDING"
    assert data["payment_status"] == "PENDING"
    assert data["payment_method"] == "CASH_ON_DELIVERY"
    assert data["restaurant_name"] == sample_restaurant.name
    assert len(data["order_items"]) == 2
    assert len(data["status_history"]) == 1
    assert data["status_history"][0]["new_status"] == "PENDING"


def test_place_order_idempotency_duplicate_submission(client, customer_headers, sample_restaurant, burger_item):
    """Submitting the same idempotency key returns the existing order rather than creating a duplicate."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel A, Room 101",
        "payment_method": "CASH_ON_DELIVERY",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
        "idempotency_key": "unique-idempotency-key-abc",
    }
    # First submit
    res1 = client.post("/api/orders", json=payload, headers=customer_headers)
    assert res1.status_code == 201
    order1 = res1.json()

    # Second submit with same key
    res2 = client.post("/api/orders", json=payload, headers=customer_headers)
    assert res2.status_code == 201 or res2.status_code == 200
    order2 = res2.json()

    assert order1["id"] == order2["id"]


def test_place_order_closed_restaurant(client, customer_headers, sample_restaurant, burger_item, db_session):
    """Attempting to order from a closed restaurant is rejected."""
    sample_restaurant.is_open = False
    db_session.commit()

    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel C, Room 202",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    response = client.post("/api/orders", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "closed" in response.json()["detail"].lower()


def test_place_order_unavailable_item(client, customer_headers, sample_restaurant, burger_item, db_session):
    """Attempting to order an out-of-stock item is rejected."""
    burger_item.is_available = False
    db_session.commit()

    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel D, Room 105",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    response = client.post("/api/orders", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "unavailable" in response.json()["detail"].lower() or "sold out" in response.json()["detail"].lower()


def test_place_order_cross_restaurant_item(client, customer_headers, sample_restaurant, pizza_item):
    """Ordering items that do not belong to the selected restaurant is rejected."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel E, Room 404",
        "items": [{"menu_item_id": str(pizza_item.id), "quantity": 1}],
    }
    response = client.post("/api/orders", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "belong" in response.json()["detail"].lower()


def test_place_order_empty_items(client, customer_headers, sample_restaurant):
    """Empty items array is rejected by validation."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel F, Room 505",
        "items": [],
    }
    response = client.post("/api/orders", json=payload, headers=customer_headers)
    assert response.status_code == 422


def test_place_order_unauthenticated(client, sample_restaurant, burger_item):
    """Unauthenticated users cannot place orders."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel G, Room 101",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 401


def test_place_order_non_customer(client, owner_headers, sample_restaurant, burger_item):
    """Non-customers (e.g. restaurant owner) cannot place orders."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Staff Quarters 12",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    response = client.post("/api/orders", json=payload, headers=owner_headers)
    assert response.status_code == 403


# ==============================================================================
# ORDER HISTORY & RETRIEVAL TESTS
# ==============================================================================

def test_get_my_orders(client, customer_headers, sample_restaurant, burger_item):
    """Customer can fetch their order history."""
    # Place order
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel H, Room 111",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    client.post("/api/orders", json=payload, headers=customer_headers)

    response = client.get("/api/orders/my-orders", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["orders"]) >= 1
    assert data["orders"][0]["delivery_address"] == "Hostel H, Room 111"


def test_get_order_detail_and_idor(
    client, customer_headers, other_customer_headers, sample_restaurant, burger_item
):
    """Customer can view their own order detail, but other customers cannot (IDOR protection)."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel J, Room 222",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    create_res = client.post("/api/orders", json=payload, headers=customer_headers)
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Owner customer fetches detail
    res_owner = client.get(f"/api/orders/{order_id}", headers=customer_headers)
    assert res_owner.status_code == 200
    assert res_owner.json()["id"] == order_id

    # Another customer attempts to view order (IDOR)
    res_other = client.get(f"/api/orders/{order_id}", headers=other_customer_headers)
    assert res_other.status_code == 403


# ==============================================================================
# ORDER CANCELLATION TESTS
# ==============================================================================

def test_cancel_pending_order_success(client, customer_headers, sample_restaurant, burger_item):
    """Customer cancels a pending order successfully."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel K, Room 333",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    create_res = client.post("/api/orders", json=payload, headers=customer_headers)
    order_id = create_res.json()["id"]

    cancel_res = client.patch(
        f"/api/orders/{order_id}/cancel",
        json={"reason": "Placed by mistake"},
        headers=customer_headers,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["order_status"] == "CANCELLED"

    # Status history should now contain PENDING then CANCELLED
    history = cancel_res.json()["status_history"]
    assert len(history) == 2
    assert history[1]["new_status"] == "CANCELLED"


def test_cancel_already_cancelled_order(client, customer_headers, sample_restaurant, burger_item):
    """Cancelling an already cancelled order returns 400 error."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel L, Room 444",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    create_res = client.post("/api/orders", json=payload, headers=customer_headers)
    order_id = create_res.json()["id"]

    client.patch(f"/api/orders/{order_id}/cancel", headers=customer_headers)
    second_cancel = client.patch(f"/api/orders/{order_id}/cancel", headers=customer_headers)
    assert second_cancel.status_code == 400
    assert "already" in second_cancel.json()["detail"].lower() and "cancel" in second_cancel.json()["detail"].lower()


def test_cancel_order_idor_protection(
    client, customer_headers, other_customer_headers, sample_restaurant, burger_item
):
    """Another customer cannot cancel someone else's order (IDOR protection)."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel M, Room 555",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    create_res = client.post("/api/orders", json=payload, headers=customer_headers)
    order_id = create_res.json()["id"]

    cancel_res = client.patch(
        f"/api/orders/{order_id}/cancel",
        headers=other_customer_headers,
    )
    assert cancel_res.status_code == 403
