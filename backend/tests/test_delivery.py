import uuid
from decimal import Decimal
import pytest
from app.models import MenuItem, Restaurant, Order
from app.models.enums import FoodCategory, OrderStatus, PaymentMethod, PaymentStatus, PartnerAvailability, DeliveryStatus


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
def ready_order(client, customer_headers, owner_headers, sample_restaurant, burger_item) -> dict:
    """Creates a sample order and advances it to READY_FOR_PICKUP."""
    # 1. Customer places order (Subtotal: 17.00, Fee: 2.00, Total: 19.00)
    payload = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel B, Room 304, Campus North",
        "payment_method": "CASH_ON_DELIVERY",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 2}],
    }
    place_res = client.post("/api/orders", json=payload, headers=customer_headers)
    assert place_res.status_code == 201
    order_id = place_res.json()["id"]

    # 2. Restaurant accepts order
    acc_res = client.patch(f"/api/restaurant/orders/{order_id}/accept", headers=owner_headers)
    assert acc_res.status_code == 200

    # 3. Restaurant starts preparation
    prep_res = client.patch(f"/api/restaurant/orders/{order_id}/start-preparation", headers=owner_headers)
    assert prep_res.status_code == 200

    # 4. Restaurant marks ready for pickup
    ready_res = client.patch(f"/api/restaurant/orders/{order_id}/ready-for-pickup", headers=owner_headers)
    assert ready_res.status_code == 200
    return ready_res.json()


# ==============================================================================
# 1. REGISTRATION & PROFILE TESTS
# ==============================================================================

def test_register_delivery_partner(client):
    """Verify delivery partner registration with vehicle info."""
    payload = {
        "full_name": "Rider Jack",
        "email": "rider.jack@campusbyte.com",
        "phone_number": "+1555444333",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "vehicle_type": "SCOOTER",
        "vehicle_registration_number": "CAMPUS-SCOOT-7",
    }
    res = client.post("/api/auth/register/delivery-partner", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "rider.jack@campusbyte.com"
    assert data["role"] == "DELIVERY_PARTNER"
    assert "password_hash" not in data


def test_register_delivery_partner_validation(client):
    """Validation errors: password mismatch and duplicate email."""
    payload = {
        "full_name": "Rider Jane",
        "email": "rider.jane@campusbyte.com",
        "phone_number": "+1555444222",
        "password": "Password123!",
        "confirm_password": "WrongPassword123!",
        "vehicle_type": "BICYCLE",
    }
    res = client.post("/api/auth/register/delivery-partner", json=payload)
    assert res.status_code == 422

    # Duplicate email
    payload["confirm_password"] = payload["password"]
    first = client.post("/api/auth/register/delivery-partner", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register/delivery-partner", json=payload)
    assert second.status_code == 409


def test_get_and_update_delivery_profile(client, delivery_headers, sample_delivery_profile):
    """Delivery partner inspects and updates their profile."""
    res = client.get("/api/delivery/profile", headers=delivery_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "dave.courier@campusbyte.com"
    assert data["vehicle_type"] == "BICYCLE"
    assert data["availability_status"] == "AVAILABLE"

    # Update profile
    patch_res = client.patch(
        "/api/delivery/profile",
        json={
            "vehicle_type": "MOTORCYCLE",
            "vehicle_registration_number": "MOTO-888",
            "phone_number": "+1777000111",
        },
        headers=delivery_headers,
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["vehicle_type"] == "MOTORCYCLE"
    assert updated["vehicle_registration_number"] == "MOTO-888"


# ==============================================================================
# 2. AVAILABILITY MANAGEMENT TESTS
# ==============================================================================

def test_delivery_partner_availability_toggle(client, delivery_headers, sample_delivery_profile):
    """Toggle between OFFLINE and AVAILABLE."""
    # Go OFFLINE
    res = client.patch(
        "/api/delivery/availability",
        json={"availability_status": "OFFLINE"},
        headers=delivery_headers,
    )
    assert res.status_code == 200
    assert res.json()["availability_status"] == "OFFLINE"
    assert res.json()["is_available"] is False

    # Go AVAILABLE
    res2 = client.patch(
        "/api/delivery/availability",
        json={"availability_status": "AVAILABLE"},
        headers=delivery_headers,
    )
    assert res2.status_code == 200
    assert res2.json()["availability_status"] == "AVAILABLE"
    assert res2.json()["is_available"] is True


def test_delivery_partner_availability_blocked_during_active_delivery(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Cannot set availability to OFFLINE or AVAILABLE while active delivery is in progress."""
    order_id = ready_order["id"]
    accept_res = client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)
    assert accept_res.status_code == 201

    # Attempt to go OFFLINE while delivery is active
    res = client.patch(
        "/api/delivery/availability",
        json={"availability_status": "OFFLINE"},
        headers=delivery_headers,
    )
    assert res.status_code == 400
    assert "active delivery" in res.json()["detail"].lower()


# ==============================================================================
# 3. AVAILABLE ORDERS & CLAIMING TESTS
# ==============================================================================

def test_get_available_orders_when_available(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Partner in AVAILABLE state retrieves ready orders."""
    res = client.get("/api/delivery/available-orders", headers=delivery_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    orders = data["orders"]
    matching = [o for o in orders if o["order_id"] == ready_order["id"]]
    assert len(matching) == 1
    assert matching[0]["restaurant_name"] == "Campus Grill & Cafe"
    assert matching[0]["item_count"] == 2


def test_get_available_orders_blocked_when_offline(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Partner in OFFLINE state cannot browse orders."""
    client.patch(
        "/api/delivery/availability",
        json={"availability_status": "OFFLINE"},
        headers=delivery_headers,
    )
    res = client.get("/api/delivery/available-orders", headers=delivery_headers)
    assert res.status_code == 400
    assert "AVAILABLE" in res.json()["detail"]


def test_accept_delivery_request_success(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Claiming an eligible order transitions partner to BUSY and creates assignment."""
    order_id = ready_order["id"]
    res = client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["order_id"] == order_id
    assert data["delivery_status"] == "ASSIGNED"
    assert data["order_status"] == "READY_FOR_PICKUP"

    # Verify partner is now BUSY
    prof = client.get("/api/delivery/profile", headers=delivery_headers).json()
    assert prof["availability_status"] == "BUSY"


def test_accept_delivery_request_already_claimed_conflict(
    client, delivery_headers, sample_delivery_profile, other_delivery_headers, other_delivery_profile, ready_order
):
    """Second courier receives 409 Conflict when attempting to claim an already accepted order."""
    order_id = ready_order["id"]
    res1 = client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)
    assert res1.status_code == 201

    # Second courier attempts to accept
    res2 = client.post(f"/api/delivery/assignments/{order_id}/accept", headers=other_delivery_headers)
    assert res2.status_code == 409
    assert "already been claimed" in res2.json()["detail"]


def test_accept_delivery_request_while_already_busy(
    client, delivery_headers, sample_delivery_profile, ready_order, burger_item, sample_restaurant, customer_headers, owner_headers
):
    """Courier cannot accept a second order while an active delivery is in progress."""
    # Claim first order
    order_id = ready_order["id"]
    client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)

    # Create a second ready order
    p2 = {
        "restaurant_id": str(sample_restaurant.id),
        "delivery_address": "Hostel C, Room 101",
        "payment_method": "CASH_ON_DELIVERY",
        "items": [{"menu_item_id": str(burger_item.id), "quantity": 1}],
    }
    o2_id = client.post("/api/orders", json=p2, headers=customer_headers).json()["id"]
    client.patch(f"/api/restaurant/orders/{o2_id}/accept", headers=owner_headers)
    client.patch(f"/api/restaurant/orders/{o2_id}/start-preparation", headers=owner_headers)
    client.patch(f"/api/restaurant/orders/{o2_id}/ready-for-pickup", headers=owner_headers)

    # Attempt to claim second order
    res = client.post(f"/api/delivery/assignments/{o2_id}/accept", headers=delivery_headers)
    assert res.status_code == 400
    assert "active delivery" in res.json()["detail"] or "AVAILABLE" in res.json()["detail"]


# ==============================================================================
# 4. LIFECYCLE: PICKUP -> OUT FOR DELIVERY -> COD -> COMPLETE
# ==============================================================================

def test_full_delivery_lifecycle_with_cod(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Test full courier delivery flow: Accept -> Pickup -> Out for Delivery -> COD -> Delivered."""
    order_id = ready_order["id"]

    # 1. Accept
    res_acc = client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)
    assert res_acc.status_code == 201

    # Check active delivery endpoint
    active_res = client.get("/api/delivery/active-delivery", headers=delivery_headers)
    assert active_res.status_code == 200
    assert active_res.json()["order_id"] == order_id

    # 2. Confirm Restaurant Pickup
    pickup_res = client.patch(f"/api/delivery/assignments/{order_id}/pickup", headers=delivery_headers)
    assert pickup_res.status_code == 200
    assert pickup_res.json()["order_status"] == "PICKED_UP"
    assert pickup_res.json()["delivery_status"] == "PICKED_UP"
    assert pickup_res.json()["picked_up_at"] is not None

    # Cannot pickup again
    dup_pickup = client.patch(f"/api/delivery/assignments/{order_id}/pickup", headers=delivery_headers)
    assert dup_pickup.status_code == 400

    # 3. Start Out for Delivery
    start_res = client.patch(f"/api/delivery/assignments/{order_id}/start-delivery", headers=delivery_headers)
    assert start_res.status_code == 200
    assert start_res.json()["order_status"] == "OUT_FOR_DELIVERY"
    assert start_res.json()["delivery_status"] == "OUT_FOR_DELIVERY"

    # 4. Check COD Status & Confirm COD Collection
    cod_status = client.get(f"/api/delivery/assignments/{order_id}/cod-status", headers=delivery_headers)
    assert cod_status.status_code == 200
    assert cod_status.json()["is_cod"] is True
    assert cod_status.json()["cod_collected"] is False
    total_amount = Decimal(str(cod_status.json()["total_amount"]))

    # Confirm COD with mismatching amount -> 400
    bad_cod = client.post(
        f"/api/delivery/assignments/{order_id}/confirm-cod",
        json={"confirm_cash_collected": True, "collected_amount": 5.00},
        headers=delivery_headers,
    )
    assert bad_cod.status_code == 400

    # Confirm COD with correct amount -> 200
    good_cod = client.post(
        f"/api/delivery/assignments/{order_id}/confirm-cod",
        json={"confirm_cash_collected": True, "collected_amount": float(total_amount)},
        headers=delivery_headers,
    )
    assert good_cod.status_code == 200
    assert good_cod.json()["cod_collected"] is True
    assert good_cod.json()["payment_status"] == "PAID"

    # 5. Complete Delivery
    comp_res = client.patch(
        f"/api/delivery/assignments/{order_id}/complete",
        json={"confirm_delivered": True},
        headers=delivery_headers,
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["order_status"] == "DELIVERED"
    assert comp_res.json()["delivery_status"] == "DELIVERED"

    # Courier availability resets to AVAILABLE
    prof = client.get("/api/delivery/profile", headers=delivery_headers).json()
    assert prof["availability_status"] == "AVAILABLE"
    assert prof["is_available"] is True

    # Active delivery is now cleared
    active_res2 = client.get("/api/delivery/active-delivery", headers=delivery_headers)
    assert active_res2.status_code == 200
    assert active_res2.json() is None


def test_complete_delivery_cod_enforcement(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Attempting to complete COD delivery without cash collection confirmation is rejected."""
    order_id = ready_order["id"]
    client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)
    client.patch(f"/api/delivery/assignments/{order_id}/pickup", headers=delivery_headers)
    client.patch(f"/api/delivery/assignments/{order_id}/start-delivery", headers=delivery_headers)

    # Attempt to complete without COD confirmation
    res = client.patch(
        f"/api/delivery/assignments/{order_id}/complete",
        json={"confirm_delivered": True, "confirm_cash_collected": False},
        headers=delivery_headers,
    )
    assert res.status_code == 400
    assert "cash on delivery" in res.json()["detail"].lower()


# ==============================================================================
# 5. IDOR & ACCESS CONTROL TESTS
# ==============================================================================

def test_delivery_idor_protection(
    client, delivery_headers, sample_delivery_profile, other_delivery_headers, other_delivery_profile, ready_order
):
    """Courier B cannot view or transition Courier A's active assignment."""
    order_id = ready_order["id"]
    client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)

    # Courier B attempts to view assignment details
    idor_get = client.get(f"/api/delivery/assignments/{order_id}", headers=other_delivery_headers)
    assert idor_get.status_code == 403

    # Courier B attempts to confirm pickup
    idor_pickup = client.patch(f"/api/delivery/assignments/{order_id}/pickup", headers=other_delivery_headers)
    assert idor_pickup.status_code == 403


def test_delivery_endpoints_role_guard(client, customer_headers, owner_headers):
    """Customers and Restaurant Owners cannot access courier endpoints."""
    # Customer
    res1 = client.get("/api/delivery/profile", headers=customer_headers)
    assert res1.status_code == 403

    # Restaurant Owner
    res2 = client.get("/api/delivery/available-orders", headers=owner_headers)
    assert res2.status_code == 403


# ==============================================================================
# 6. HISTORY, STATISTICS & SYSTEM SYNCHRONIZATION
# ==============================================================================

def test_delivery_history_and_statistics(
    client, delivery_headers, sample_delivery_profile, ready_order
):
    """Verify statistics and history tracking after successful delivery."""
    order_id = ready_order["id"]
    client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)
    client.patch(f"/api/delivery/assignments/{order_id}/pickup", headers=delivery_headers)
    client.patch(f"/api/delivery/assignments/{order_id}/start-delivery", headers=delivery_headers)
    client.post(
        f"/api/delivery/assignments/{order_id}/confirm-cod",
        json={"confirm_cash_collected": True, "collected_amount": 19.00},
        headers=delivery_headers,
    )
    client.patch(
        f"/api/delivery/assignments/{order_id}/complete",
        json={"confirm_delivered": True},
        headers=delivery_headers,
    )

    # History API
    hist_res = client.get("/api/delivery/history", headers=delivery_headers)
    assert hist_res.status_code == 200
    assert hist_res.json()["total"] >= 1
    assert hist_res.json()["items"][0]["order_status"] == "DELIVERED"
    assert hist_res.json()["items"][0]["cod_collected"] is True

    # Order status history timeline endpoint
    timeline_res = client.get(f"/api/delivery/assignments/{order_id}/history", headers=delivery_headers)
    assert timeline_res.status_code == 200
    history = timeline_res.json()
    statuses = [h["new_status"] for h in history]
    assert "PICKED_UP" in statuses
    assert "OUT_FOR_DELIVERY" in statuses
    assert "DELIVERED" in statuses

    # Statistics API
    stats_res = client.get("/api/delivery/dashboard/statistics", headers=delivery_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["completed_deliveries_count"] >= 1
    assert Decimal(str(stats["total_cod_collected"])) >= Decimal("19.00")


def test_customer_and_restaurant_synchronization(
    client, customer_headers, owner_headers, delivery_headers, sample_delivery_profile, ready_order
):
    """Verify that customer tracking and restaurant dashboard reflect courier transitions."""
    order_id = ready_order["id"]

    # 1. Partner accepts
    client.post(f"/api/delivery/assignments/{order_id}/accept", headers=delivery_headers)

    # Check restaurant view
    rest_view = client.get(f"/api/restaurant/orders/{order_id}", headers=owner_headers)
    assert rest_view.status_code == 200
    assert rest_view.json()["delivery_partner_id"] is not None
    assert rest_view.json()["delivery_partner_name"] == "Dave Courier"

    # 2. Partner picks up
    client.patch(f"/api/delivery/assignments/{order_id}/pickup", headers=delivery_headers)

    # Check customer tracking view
    cust_view = client.get(f"/api/orders/{order_id}", headers=customer_headers)
    assert cust_view.status_code == 200
    assert cust_view.json()["order_status"] == "PICKED_UP"
    assert cust_view.json()["picked_up_at"] is not None
    assert cust_view.json()["delivery_partner_name"] == "Dave Courier"
    assert cust_view.json()["delivery_partner_vehicle"] == "BICYCLE"

    # 3. Partner delivers
    client.patch(f"/api/delivery/assignments/{order_id}/start-delivery", headers=delivery_headers)
    client.post(
        f"/api/delivery/assignments/{order_id}/confirm-cod",
        json={"confirm_cash_collected": True, "collected_amount": 19.00},
        headers=delivery_headers,
    )
    client.patch(f"/api/delivery/assignments/{order_id}/complete", headers=delivery_headers)

    # Final verification on customer view
    final_cust = client.get(f"/api/orders/{order_id}", headers=customer_headers).json()
    assert final_cust["order_status"] == "DELIVERED"
    assert final_cust["delivered_at"] is not None
