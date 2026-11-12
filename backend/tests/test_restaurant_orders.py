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
def other_restaurant(db_session, other_owner) -> Restaurant:
    """A secondary restaurant for other_owner."""
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
def pending_order(client, customer_headers, sample_restaurant, burger_item) -> dict:
    """Creates a sample pending order for sample_restaurant via customer API."""
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel B, Room 304, Campus North",
        "payment_method": "CASH_ON_DELIVERY",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 2}],
    }
    res = client.post("/api/orders", json=payload, headers=customer_headers)
    assert res.status_code == 201
    return res.json()


# ==============================================================================
# RESTAURANT ORDER LISTING & PERMISSION TESTS
# ==============================================================================

def test_list_restaurant_orders(client, owner_headers, pending_order):
    """Owner lists incoming orders for their restaurant."""
    res = client.get("/api/restaurant/orders", headers=owner_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    orders = data["orders"]
    matching = [o for o in orders if o["id"] == pending_order["id"]]
    assert len(matching) == 1
    assert matching[0]["customer_name"] == "Alice Student"
    assert matching[0]["order_status"] == "PENDING"
    assert float(matching[0]["total_amount"]) == 19.00  # 2 x 8.50 + 2.00 delivery


def test_list_restaurant_orders_filter_and_search(client, owner_headers, pending_order):
    """Filter orders by status and search by order ID substring."""
    order_id = pending_order["id"]
    prefix = order_id[:8]

    # Filter by status=PENDING
    res_status = client.get("/api/restaurant/orders?status=PENDING", headers=owner_headers)
    assert res_status.status_code == 200
    assert any(o["id"] == order_id for o in res_status.json()["orders"])

    # Filter by status=DELIVERED (should not contain pending order)
    res_delivered = client.get("/api/restaurant/orders?status=DELIVERED", headers=owner_headers)
    assert res_delivered.status_code == 200
    assert not any(o["id"] == order_id for o in res_delivered.json()["orders"])

    # Search by partial ID
    res_search = client.get(f"/api/restaurant/orders?search={prefix}", headers=owner_headers)
    assert res_search.status_code == 200
    assert any(o["id"] == order_id for o in res_search.json()["orders"])


def test_list_restaurant_orders_idor(client, other_owner_headers, other_restaurant, pending_order):
    """Another restaurant owner cannot see sample_restaurant's orders."""
    res = client.get("/api/restaurant/orders", headers=other_owner_headers)
    assert res.status_code == 200
    data = res.json()
    assert not any(o["id"] == pending_order["id"] for o in data["orders"])


def test_restaurant_orders_access_control(client, customer_headers, delivery_headers, pending_order):
    """Customers and delivery partners cannot access restaurant order APIs."""
    # Customer
    res_cust = client.get("/api/restaurant/orders", headers=customer_headers)
    assert res_cust.status_code == 403

    # Delivery Partner
    res_del = client.get("/api/restaurant/orders", headers=delivery_headers)
    assert res_del.status_code == 403

    # Unauthenticated
    res_unauth = client.get("/api/restaurant/orders")
    assert res_unauth.status_code == 401


def test_get_restaurant_order_detail(client, owner_headers, other_owner_headers, other_restaurant, pending_order):
    """Owner retrieves single order detail with customer contact info; other owner blocked."""
    order_id = pending_order["id"]

    res_owner = client.get(f"/api/restaurant/orders/{order_id}", headers=owner_headers)
    assert res_owner.status_code == 200
    data = res_owner.json()
    assert data["id"] == order_id
    assert data["customer_name"] == "Alice Student"
    assert data["customer_phone"] == "+1987654321"
    assert len(data["order_items"]) == 1

    # IDOR check: other owner cannot access
    res_other = client.get(f"/api/restaurant/orders/{order_id}", headers=other_owner_headers)
    assert res_other.status_code == 403


def test_get_restaurant_order_statistics(client, owner_headers, pending_order):
    """Calculates real order statistics across all lifecycle states."""
    res = client.get("/api/restaurant/orders/statistics", headers=owner_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_orders"] >= 1
    assert data["pending_orders"] >= 1
    assert "accepted_orders" in data
    assert "preparing_orders" in data
    assert "ready_for_pickup_orders" in data


def test_get_new_orders_notifications(client, owner_headers, pending_order):
    """Incremental polling returns newly placed pending orders."""
    res = client.get("/api/restaurant/orders/notifications", headers=owner_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["new_orders_count"] >= 1
    assert any(o["id"] == pending_order["id"] for o in data["pending_orders"])


# ==============================================================================
# ORDER ACCEPTANCE TESTS
# ==============================================================================

def test_accept_order_success(client, owner_headers, pending_order):
    """Owner accepts a pending order successfully."""
    order_id = pending_order["id"]
    res = client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["order_status"] == "ACCEPTED"
    assert data["accepted_at"] is not None

    # Check status history
    history = data["status_history"]
    assert len(history) >= 2
    assert history[-1]["new_status"] == "ACCEPTED"
    assert history[-1]["changed_by_role"] == "RESTAURANT_OWNER"


def test_accept_order_duplicate_rejected(client, owner_headers, pending_order):
    """Attempting to accept an already accepted order is rejected with 400."""
    order_id = pending_order["id"]
    client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)

    res_duplicate = client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)
    assert res_duplicate.status_code == 400
    assert "already been accepted" in res_duplicate.json()["detail"].lower()


def test_accept_order_by_other_owner_idor(client, other_owner_headers, other_restaurant, pending_order):
    """Another owner cannot accept this restaurant's order (IDOR)."""
    order_id = pending_order["id"]
    res = client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=other_owner_headers)
    assert res.status_code == 403


# ==============================================================================
# ORDER REJECTION TESTS
# ==============================================================================

def test_reject_order_success(client, owner_headers, customer_headers, pending_order):
    """Owner rejects pending order with mandatory reason; customer sees rejection info."""
    order_id = pending_order["id"]
    payload = {"reason": "Kitchen closed early due to maintenance"}
    res = client.patch(f"/api/restaurant/orders/{order_id}/reject", json=payload, headers=owner_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["order_status"] == "REJECTED"
    assert data["rejection_reason"] == "Kitchen closed early due to maintenance"
    assert data["rejected_at"] is not None

    # Verify customer can view rejection details
    res_cust = client.get(f"/api/orders/{order_id}", headers=customer_headers)
    assert res_cust.status_code == 200
    cust_data = res_cust.json()
    assert cust_data["order_status"] == "REJECTED"
    assert cust_data["rejection_reason"] == "Kitchen closed early due to maintenance"


def test_reject_order_validation(client, owner_headers, pending_order):
    """Rejection requires valid reason with minimum length 5."""
    order_id = pending_order["id"]

    # Short reason
    res_short = client.patch(
        f"/api/restaurant/orders/{order_id}/reject",
        json={"reason": "No"},
        headers=owner_headers,
    )
    assert res_short.status_code == 422

    # Missing reason
    res_missing = client.patch(
        f"/api/restaurant/orders/{order_id}/reject",
        json={},
        headers=owner_headers,
    )
    assert res_missing.status_code == 422


def test_reject_already_accepted_order_fails(client, owner_headers, pending_order):
    """Cannot reject an order that has already been accepted."""
    order_id = pending_order["id"]
    client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)

    res_reject = client.patch(
        f"/api/restaurant/orders/{order_id}/reject",
        json={"reason": "Cannot prepare this dish now"},
        headers=owner_headers,
    )
    assert res_reject.status_code == 400
    assert "cannot reject" in res_reject.json()["detail"].lower()


# ==============================================================================
# PREPARATION & READY FOR PICKUP TESTS
# ==============================================================================

def test_start_preparation_and_ready_for_pickup(client, owner_headers, pending_order):
    """Full preparation lifecycle: PENDING -> ACCEPTED -> PREPARING -> READY_FOR_PICKUP."""
    order_id = pending_order["id"]

    # 1. Accept
    res_accept = client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)
    assert res_accept.status_code == 200

    # 2. Start Preparation
    res_prep = client.patch(f"/api/restaurant/orders/{order_id}/start-preparation", headers=owner_headers)
    assert res_prep.status_code == 200
    assert res_prep.json()["order_status"] == "PREPARING"
    assert res_prep.json()["preparing_at"] is not None

    # 3. Mark Ready for Pickup
    res_ready = client.patch(f"/api/restaurant/orders/{order_id}/ready-for-pickup", headers=owner_headers)
    assert res_ready.status_code == 200
    assert res_ready.json()["order_status"] == "READY_FOR_PICKUP"
    assert res_ready.json()["ready_for_pickup_at"] is not None


def test_invalid_preparation_transitions(client, owner_headers, pending_order):
    """Cannot jump directly from PENDING to PREPARING or READY_FOR_PICKUP."""
    order_id = pending_order["id"]

    # Attempt to start prep on PENDING order
    res_prep = client.patch(f"/api/restaurant/orders/{order_id}/start-preparation", headers=owner_headers)
    assert res_prep.status_code == 400
    assert "must be accepted" in res_prep.json()["detail"].lower()

    # Attempt to mark ready on PENDING order
    res_ready = client.patch(f"/api/restaurant/orders/{order_id}/ready-for-pickup", headers=owner_headers)
    assert res_ready.status_code == 400
    assert "must be in preparation" in res_ready.json()["detail"].lower()


# ==============================================================================
# CONCURRENCY & STATUS HISTORY TESTS
# ==============================================================================

def test_customer_cancel_vs_owner_accept_concurrency(client, owner_headers, customer_headers, sample_restaurant, burger_item):
    """If customer cancels first, owner cannot accept."""
    # Place order
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel B, Room 101",
        "payment_method": "CASH_ON_DELIVERY",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    create_res = client.post("/api/orders", json=payload, headers=customer_headers)
    order_id = create_res.json()["id"]

    # Customer cancels
    client.patch(f"/api/orders/{order_id}/cancel", headers=customer_headers)

    # Owner attempts to accept cancelled order
    res_accept = client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)
    assert res_accept.status_code == 400
    assert "cancelled" in res_accept.json()["detail"].lower()


def test_order_history_endpoint(client, owner_headers, pending_order):
    """Audit history endpoint returns chronological transitions."""
    order_id = pending_order["id"]
    client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)
    client.patch(f"/api/restaurant/orders/{order_id}/start-preparation", headers=owner_headers)

    res_history = client.get(f"/api/restaurant/orders/{order_id}/history", headers=owner_headers)
    assert res_history.status_code == 200
    history = res_history.json()
    assert len(history) == 3
    assert history[0]["new_status"] == "PENDING"
    assert history[1]["new_status"] == "ACCEPTED"
    assert history[2]["new_status"] == "PREPARING"
