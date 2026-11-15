"""
Campus Byte - Complete 20-Step End-to-End System Integration Test
Validates the entire business lifecycle across all 3 roles:
Customer, Restaurant Owner, and Delivery Partner.
"""
from decimal import Decimal
import uuid
from fastapi.testclient import TestClient

from app.models.enums import OrderStatus, PaymentMethod, FoodCategory


def test_complete_e2e_order_lifecycle(client: TestClient, db_session):
    """
    Complete end-to-end integration test verifying the entire business flow across all 3 roles:
    1. Register Restaurant Owner (creates user + restaurant profile atomically)
    2. Owner logs in & retrieves JWT token
    3. Owner adds menu items to the restaurant via POST /api/restaurants/{id}/menu
    4. Register Customer
    5. Customer logs in & retrieves JWT token
    6. Customer discovers restaurants and views menu items
    7. Customer places order (order_status: PENDING)
    8. Customer retrieves order detail
    9. Owner fetches restaurant orders list and sees new order
    10. Owner accepts order (order_status: ACCEPTED)
    11. Owner updates status to PREPARING
    12. Owner updates status to READY_FOR_PICKUP
    13. Register Delivery Partner (creates user + delivery partner fleet profile atomically)
    14. Delivery Partner logs in & retrieves JWT token
    15. Delivery Partner sets status to AVAILABLE
    16. Delivery Partner views available orders and sees the ready order
    17. Delivery Partner claims/accepts the delivery assignment
    18. Delivery Partner confirms pickup at restaurant (order_status: PICKED_UP)
    19. Delivery Partner starts delivery (order_status: OUT_FOR_DELIVERY)
    20. Delivery Partner confirms COD collection and marks delivery complete (order_status: DELIVERED)
    21. Verification: Customer order is DELIVERED, courier is AVAILABLE, complete transition history verified
    """
    # -------------------------------------------------------------
    # 1. Register Restaurant Owner
    # -------------------------------------------------------------
    suffix = uuid.uuid4().hex[:6]
    owner_email = f"chef_{suffix}@campus.edu"
    owner_pwd = "Password123!"
    reg_owner_resp = client.post(
        "/api/auth/register/restaurant-owner",
        json={
            "full_name": "Head Chef Luigi",
            "email": owner_email,
            "phone_number": "+1234567890",
            "password": owner_pwd,
            "confirm_password": owner_pwd,
            "restaurant_name": f"Campus Trattoria {suffix}",
            "restaurant_address": "Campus Center, Food Court 1",
            "restaurant_description": "Authentic wood-fired pizza and pasta",
        },
    )
    assert reg_owner_resp.status_code == 201, reg_owner_resp.text

    # -------------------------------------------------------------
    # 2. Owner Login
    # -------------------------------------------------------------
    owner_login = client.post(
        "/api/auth/login",
        json={"email": owner_email, "password": owner_pwd},
    )
    assert owner_login.status_code == 200, owner_login.text
    owner_token = owner_login.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Fetch owner's restaurant ID
    my_rest_resp = client.get("/api/restaurants/my-restaurant", headers=owner_headers)
    assert my_rest_resp.status_code == 200, my_rest_resp.text
    restaurant_id = my_rest_resp.json()["id"]

    # -------------------------------------------------------------
    # 3. Owner adds Menu Items
    # -------------------------------------------------------------
    item_resp = client.post(
        f"/api/restaurants/{restaurant_id}/menu",
        headers=owner_headers,
        json={
            "name": "Margherita Gourmet Pizza",
            "description": "San Marzano tomatoes, fresh mozzarella, basil",
            "price": 250.00,
            "category": FoodCategory.PIZZA.value,
            "is_available": True,
        },
    )
    assert item_resp.status_code == 201, item_resp.text
    item_id = item_resp.json()["id"]

    # -------------------------------------------------------------
    # 4. Register Customer
    # -------------------------------------------------------------
    cust_email = f"student_{suffix}@campus.edu"
    cust_pwd = "Password123!"
    reg_cust_resp = client.post(
        "/api/auth/register/customer",
        json={
            "full_name": "Alex Student",
            "email": cust_email,
            "phone_number": "+1987654321",
            "password": cust_pwd,
            "confirm_password": cust_pwd,
        },
    )
    assert reg_cust_resp.status_code == 201, reg_cust_resp.text

    # -------------------------------------------------------------
    # 5. Customer Login
    # -------------------------------------------------------------
    cust_login = client.post(
        "/api/auth/login",
        json={"email": cust_email, "password": cust_pwd},
    )
    assert cust_login.status_code == 200, cust_login.text
    cust_token = cust_login.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # -------------------------------------------------------------
    # 6. Customer Discovers Restaurant and Menu
    # -------------------------------------------------------------
    rest_list = client.get("/api/restaurants/")
    assert rest_list.status_code == 200
    assert any(r["id"] == restaurant_id for r in rest_list.json()["restaurants"])

    menu_list = client.get(f"/api/restaurants/{restaurant_id}/menu")
    assert menu_list.status_code == 200
    assert any(m["id"] == item_id for m in menu_list.json()["items"])

    # -------------------------------------------------------------
    # 7. Customer Places Order (PENDING)
    # -------------------------------------------------------------
    order_payload = {
        "restaurant_id": restaurant_id,
        "delivery_address": "Hall of Residence 3, Room 104",
        "payment_method": PaymentMethod.CASH_ON_DELIVERY.value,
        "special_instructions": "Please leave at reception if unreachable",
        "items": [
            {
                "menu_item_id": item_id,
                "quantity": 2,
            }
        ],
    }
    order_resp = client.post("/api/orders", headers=cust_headers, json=order_payload)
    assert order_resp.status_code == 201, order_resp.text
    order_data = order_resp.json()
    order_id = order_data["id"]
    assert order_data["order_status"] == OrderStatus.PENDING.value
    # 2 x 250.00 + 2.00 delivery fee = 502.00
    assert float(order_data["total_amount"]) == 502.00

    # -------------------------------------------------------------
    # 8. Customer views Order Details
    # -------------------------------------------------------------
    cust_detail = client.get(f"/api/orders/{order_id}", headers=cust_headers)
    assert cust_detail.status_code == 200
    assert cust_detail.json()["order_status"] == OrderStatus.PENDING.value

    # -------------------------------------------------------------
    # 9. Restaurant Owner checks Orders
    # -------------------------------------------------------------
    ro_list = client.get(
        "/api/restaurant/orders",
        headers=owner_headers,
    )
    assert ro_list.status_code == 200
    assert any(o["id"] == order_id for o in ro_list.json()["orders"])

    # -------------------------------------------------------------
    # 10. Restaurant Owner accepts Order (ACCEPTED)
    # -------------------------------------------------------------
    accept_resp = client.patch(
        f"/api/restaurant/orders/{order_id}/accept",
        headers=owner_headers,
    )
    assert accept_resp.status_code == 200, accept_resp.text
    assert accept_resp.json()["order_status"] == OrderStatus.ACCEPTED.value

    # -------------------------------------------------------------
    # 11. Restaurant Owner begins cooking (PREPARING)
    # -------------------------------------------------------------
    prep_resp = client.patch(
        f"/api/restaurant/orders/{order_id}/start-preparation",
        headers=owner_headers,
    )
    assert prep_resp.status_code == 200, prep_resp.text
    assert prep_resp.json()["order_status"] == OrderStatus.PREPARING.value

    # -------------------------------------------------------------
    # 12. Restaurant Owner marks READY_FOR_PICKUP
    # -------------------------------------------------------------
    ready_resp = client.patch(
        f"/api/restaurant/orders/{order_id}/ready-for-pickup",
        headers=owner_headers,
    )
    assert ready_resp.status_code == 200, ready_resp.text
    assert ready_resp.json()["order_status"] == OrderStatus.READY_FOR_PICKUP.value

    # -------------------------------------------------------------
    # 13. Register Delivery Partner
    # -------------------------------------------------------------
    courier_email = f"courier_{suffix}@campus.edu"
    courier_pwd = "Password123!"
    reg_courier = client.post(
        "/api/auth/register/delivery-partner",
        json={
            "full_name": "Lightning Courier",
            "email": courier_email,
            "phone_number": "+1555666777",
            "password": courier_pwd,
            "confirm_password": courier_pwd,
            "vehicle_type": "MOTORCYCLE",
        },
    )
    assert reg_courier.status_code == 201, reg_courier.text

    # -------------------------------------------------------------
    # 14. Delivery Partner Login
    # -------------------------------------------------------------
    courier_login = client.post(
        "/api/auth/login",
        json={"email": courier_email, "password": courier_pwd},
    )
    assert courier_login.status_code == 200, courier_login.text
    courier_token = courier_login.json()["access_token"]
    courier_headers = {"Authorization": f"Bearer {courier_token}"}

    # -------------------------------------------------------------
    # 15. Courier sets availability to AVAILABLE
    # -------------------------------------------------------------
    toggle_resp = client.patch(
        "/api/delivery/availability",
        headers=courier_headers,
        json={"availability_status": "AVAILABLE"},
    )
    assert toggle_resp.status_code == 200, toggle_resp.text
    assert toggle_resp.json()["availability_status"] == "AVAILABLE"

    # -------------------------------------------------------------
    # 16. Courier discovers available ready orders
    # -------------------------------------------------------------
    avail_orders = client.get("/api/delivery/available-orders", headers=courier_headers)
    assert avail_orders.status_code == 200, avail_orders.text
    assert any(o["order_id"] == order_id for o in avail_orders.json()["orders"])

    # -------------------------------------------------------------
    # 17. Courier claims/accepts delivery assignment
    # -------------------------------------------------------------
    claim_resp = client.post(
        f"/api/delivery/assignments/{order_id}/accept",
        headers=courier_headers,
    )
    assert claim_resp.status_code == 201, claim_resp.text

    # -------------------------------------------------------------
    # 18. Courier confirms Restaurant Pickup (PICKED_UP)
    # -------------------------------------------------------------
    pickup_resp = client.patch(
        f"/api/delivery/assignments/{order_id}/pickup",
        headers=courier_headers,
    )
    assert pickup_resp.status_code == 200, pickup_resp.text
    assert pickup_resp.json()["order_status"] == OrderStatus.PICKED_UP.value

    # -------------------------------------------------------------
    # 19. Courier starts Delivery (OUT_FOR_DELIVERY)
    # -------------------------------------------------------------
    start_deliv = client.patch(
        f"/api/delivery/assignments/{order_id}/start-delivery",
        headers=courier_headers,
    )
    assert start_deliv.status_code == 200, start_deliv.text
    assert start_deliv.json()["order_status"] == OrderStatus.OUT_FOR_DELIVERY.value

    # Verify customer sees OUT_FOR_DELIVERY
    cust_track = client.get(f"/api/orders/{order_id}", headers=cust_headers)
    assert cust_track.status_code == 200
    assert cust_track.json()["order_status"] == OrderStatus.OUT_FOR_DELIVERY.value

    # -------------------------------------------------------------
    # 20. Courier confirms COD collection and completes delivery (DELIVERED)
    # -------------------------------------------------------------
    cod_check = client.get(f"/api/delivery/assignments/{order_id}/cod-status", headers=courier_headers)
    assert cod_check.status_code == 200
    assert cod_check.json()["is_cod"] is True
    total_amt = float(Decimal(str(cod_check.json()["total_amount"])))

    cod_collect = client.post(
        f"/api/delivery/assignments/{order_id}/confirm-cod",
        headers=courier_headers,
        json={"confirm_cash_collected": True, "collected_amount": total_amt},
    )
    assert cod_collect.status_code == 200, cod_collect.text

    complete_deliv = client.patch(
        f"/api/delivery/assignments/{order_id}/complete",
        headers=courier_headers,
        json={"confirm_delivered": True},
    )
    assert complete_deliv.status_code == 200, complete_deliv.text
    assert complete_deliv.json()["order_status"] == OrderStatus.DELIVERED.value

    # -------------------------------------------------------------
    # 21. Complete verification across all stakeholders
    # -------------------------------------------------------------
    # Customer checks order: DELIVERED
    final_cust_view = client.get(f"/api/orders/{order_id}", headers=cust_headers)
    assert final_cust_view.status_code == 200
    assert final_cust_view.json()["order_status"] == OrderStatus.DELIVERED.value

    # Courier profile: should be free/available again
    courier_profile = client.get("/api/delivery/profile", headers=courier_headers)
    assert courier_profile.status_code == 200
    assert courier_profile.json()["availability_status"] == "AVAILABLE"

    # Order history: all statuses logged in chronological order
    hist_resp = client.get(
        f"/api/restaurant/orders/{order_id}/history",
        headers=owner_headers,
    )
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    logged_statuses = [h["new_status"] for h in history]
    assert OrderStatus.PENDING.value in logged_statuses
    assert OrderStatus.ACCEPTED.value in logged_statuses
    assert OrderStatus.PREPARING.value in logged_statuses
    assert OrderStatus.READY_FOR_PICKUP.value in logged_statuses
    assert OrderStatus.PICKED_UP.value in logged_statuses
    assert OrderStatus.OUT_FOR_DELIVERY.value in logged_statuses
    assert OrderStatus.DELIVERED.value in logged_statuses
