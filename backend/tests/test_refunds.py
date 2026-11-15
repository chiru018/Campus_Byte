import uuid
from decimal import Decimal
import pytest
from app.models import (
    Order,
    OrderItem,
    MenuItem,
    Restaurant,
)
from app.models.enums import (
    OrderStatus,
    PaymentStatus,
    PaymentMethod,
    RefundIssueCategory,
    RefundStatus,
)


def create_delivered_order(db_session, customer, restaurant, amount=50.0):
    """Helper to create a delivered order."""
    dec_amount = Decimal(str(amount))
    menu_item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=restaurant.id,
        name="Loaded Pizza",
        category="PIZZA",
        price=dec_amount,
        is_available=True,
    )
    db_session.add(menu_item)
    db_session.commit()

    order = Order(
        id=uuid.uuid4(),
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        order_status=OrderStatus.DELIVERED,
        total_amount=dec_amount,
        subtotal=dec_amount,
        delivery_fee=Decimal("0.00"),
        delivery_address="Science Block B, Room 102",
        payment_method=PaymentMethod.CASH_ON_DELIVERY,
        payment_status=PaymentStatus.PAID,
    )
    db_session.add(order)
    db_session.commit()

    item = OrderItem(
        id=uuid.uuid4(),
        order_id=order.id,
        menu_item_id=menu_item.id,
        item_name=menu_item.name,
        quantity=1,
        unit_price=dec_amount,
        total_price=dec_amount,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_customer_create_refund_request_success(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Customer submits a valid refund request on a delivered order."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=60.0)

    payload = {
        "order_id": str(order.id),
        "issue_category": RefundIssueCategory.MISSING_ITEM.value,
        "description": "Side beverage and extra cheese were missing from the bag.",
        "requested_amount": 25.0,
    }

    response = client.post("/api/refunds", json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == str(order.id)
    assert data["restaurant_id"] == str(sample_restaurant.id)
    assert data["issue_category"] == RefundIssueCategory.MISSING_ITEM.value
    assert float(data["requested_amount"]) == 25.0
    assert data["status"] == RefundStatus.PENDING.value
    assert data["customer_name"] == sample_customer.full_name


def test_refund_request_undelivered_order_rejected(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Refund request is rejected if the order is not yet DELIVERED."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)
    order.order_status = OrderStatus.OUT_FOR_DELIVERY
    db_session.commit()

    payload = {
        "order_id": str(order.id),
        "issue_category": RefundIssueCategory.DAMAGED_FOOD.value,
        "description": "Food package was damaged.",
        "requested_amount": 20.0,
    }

    response = client.post("/api/refunds", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "delivered" in response.json()["detail"].lower()


def test_refund_request_amount_exceeding_total_rejected(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Requested refund amount cannot exceed order total amount."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=30.0)

    payload = {
        "order_id": str(order.id),
        "issue_category": RefundIssueCategory.POOR_QUALITY.value,
        "description": "Completely burned food.",
        "requested_amount": 45.0,  # Exceeds $30.00 total
    }

    response = client.post("/api/refunds", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "cannot exceed" in response.json()["detail"].lower()


def test_duplicate_active_refund_request_rejected(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Cannot create multiple active refund requests for the same order."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=50.0)

    payload = {
        "order_id": str(order.id),
        "issue_category": RefundIssueCategory.INCORRECT_ITEM.value,
        "description": "Received beef instead of veggie burger.",
        "requested_amount": 20.0,
    }

    res1 = client.post("/api/refunds", json=payload, headers=customer_headers)
    assert res1.status_code == 201

    res2 = client.post("/api/refunds", json=payload, headers=customer_headers)
    assert res2.status_code == 409
    assert "already exists for this order" in res2.json()["detail"].lower()


def test_refund_request_idor_foreign_order(client, db_session, sample_customer, sample_restaurant, other_customer_headers):
    """Customer B cannot request a refund on Customer A's order."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=40.0)

    payload = {
        "order_id": str(order.id),
        "issue_category": RefundIssueCategory.OTHER.value,
        "description": "Not my order",
        "requested_amount": 20.0,
    }

    response = client.post("/api/refunds", json=payload, headers=other_customer_headers)
    assert response.status_code == 403


def test_customer_view_refunds_and_idor(client, db_session, sample_customer, customer_headers, other_customer_headers, sample_restaurant):
    """Customer can view their refund requests, but other customers cannot access them."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=30.0)
    res = client.post(
        "/api/refunds",
        json={
            "order_id": str(order.id),
            "issue_category": RefundIssueCategory.DAMAGED_FOOD.value,
            "description": "Spilled soup",
            "requested_amount": 15.0,
        },
        headers=customer_headers,
    )
    refund_id = res.json()["id"]

    # Customer viewing own requests
    res_list = client.get("/api/refunds/my-requests", headers=customer_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Customer viewing own single request
    res_single = client.get(f"/api/refunds/{refund_id}", headers=customer_headers)
    assert res_single.status_code == 200
    assert res_single.json()["id"] == refund_id

    # Foreign customer tries to view -> 403
    res_idor = client.get(f"/api/refunds/{refund_id}", headers=other_customer_headers)
    assert res_idor.status_code == 403


def test_restaurant_owner_refund_lifecycle(
    client,
    db_session,
    sample_customer,
    customer_headers,
    sample_restaurant,
    owner_headers,
    other_owner_headers,
):
    """Complete restaurant owner review lifecycle: Under Review -> Approve -> Resolve, with IDOR enforcement."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=50.0)
    res = client.post(
        "/api/refunds",
        json={
            "order_id": str(order.id),
            "issue_category": RefundIssueCategory.MISSING_ITEM.value,
            "description": "Missing fries",
            "requested_amount": 15.0,
        },
        headers=customer_headers,
    )
    refund_id = res.json()["id"]

    # Foreign restaurant owner cannot view this refund
    res_foreign = client.get(f"/api/restaurant/refunds/{refund_id}", headers=other_owner_headers)
    assert res_foreign.status_code == 403

    # Restaurant owner views refund list
    res_list = client.get("/api/restaurant/refunds", headers=owner_headers)
    assert res_list.status_code == 200
    assert res_list.json()["total"] >= 1

    # Transition 1: Mark Under Review
    res_ur = client.patch(f"/api/restaurant/refunds/{refund_id}/under-review", headers=owner_headers)
    assert res_ur.status_code == 200
    assert res_ur.json()["status"] == RefundStatus.UNDER_REVIEW.value

    # Foreign owner cannot approve
    res_for_approve = client.patch(
        f"/api/restaurant/refunds/{refund_id}/approve",
        json={"approved_amount": 15.0, "owner_response": "Malicious approval attempt"},
        headers=other_owner_headers,
    )
    assert res_for_approve.status_code == 403

    # Attempt to approve an amount greater than requested -> 400
    res_over = client.patch(
        f"/api/restaurant/refunds/{refund_id}/approve",
        json={"approved_amount": 25.0, "owner_response": "Over-refund"},
        headers=owner_headers,
    )
    assert res_over.status_code == 400
    assert "cannot exceed requested amount" in res_over.json()["detail"].lower()

    # Transition 2: Legitimate Approval
    res_app = client.patch(
        f"/api/restaurant/refunds/{refund_id}/approve",
        json={"approved_amount": 15.0, "resolution_notes": "We apologize for the missing item. Refund approved."},
        headers=owner_headers,
    )
    assert res_app.status_code == 200
    assert res_app.json()["status"] == RefundStatus.APPROVED.value
    assert float(res_app.json()["approved_amount"]) == 15.0

    # Transition 3: Resolve Refund
    res_res = client.patch(
        f"/api/restaurant/refunds/{refund_id}/resolve",
        json={"resolution_notes": "Processed via UPI refund gateway txn #998811"},
        headers=owner_headers,
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == RefundStatus.RESOLVED.value
    assert res_res.json()["resolution_notes"] == "Processed via UPI refund gateway txn #998811"


def test_restaurant_owner_rejection_requires_reason(
    client,
    db_session,
    sample_customer,
    customer_headers,
    sample_restaurant,
    owner_headers,
):
    """Rejecting a refund requires a valid owner_response/explanation."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=40.0)
    res = client.post(
        "/api/refunds",
        json={
            "order_id": str(order.id),
            "issue_category": RefundIssueCategory.OTHER.value,
            "description": "Changed my mind after eating half",
            "requested_amount": 20.0,
        },
        headers=customer_headers,
    )
    refund_id = res.json()["id"]

    # Reject without explanation -> 422
    res_no_reason = client.patch(
        f"/api/restaurant/refunds/{refund_id}/reject",
        json={"explanation": "   "},
        headers=owner_headers,
    )
    assert res_no_reason.status_code == 422

    # Reject with valid explanation -> 200
    res_rej = client.patch(
        f"/api/restaurant/refunds/{refund_id}/reject",
        json={"explanation": "Food was delivered intact per courier photo evidence."},
        headers=owner_headers,
    )
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == RefundStatus.REJECTED.value
    assert "courier photo" in res_rej.json()["owner_response"]
