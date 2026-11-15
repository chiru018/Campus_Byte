import uuid
from decimal import Decimal
import pytest
from app.models import Order, OrderItem, MenuItem
from app.models.enums import OrderStatus, PaymentStatus, PaymentMethod


def create_delivered_order(db_session, customer, restaurant, amount=25.0):
    """Helper fixture to create a completed/delivered order with an item."""
    dec_amount = Decimal(str(amount))
    menu_item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=restaurant.id,
        name="Signature Burger",
        category="BURGERS",
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
        delivery_address="Hostel 4, Room 204",
        payment_method=PaymentMethod.CASH_ON_DELIVERY,
        payment_status=PaymentStatus.PAID,
    )
    db_session.add(order)
    db_session.commit()

    order_item = OrderItem(
        id=uuid.uuid4(),
        order_id=order.id,
        menu_item_id=menu_item.id,
        item_name=menu_item.name,
        quantity=1,
        unit_price=dec_amount,
        total_price=dec_amount,
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_submit_review_success(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Customer successfully submits a review on a delivered order."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)

    payload = {
        "order_id": str(order.id),
        "restaurant_id": str(sample_restaurant.id),
        "rating": 5,
        "comment": "Exceptional food quality and prompt delivery!",
    }

    response = client.post("/api/reviews", json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Exceptional food quality and prompt delivery!"
    assert data["customer_name"] == sample_customer.full_name
    assert data["order_id"] == str(order.id)
    assert data["restaurant_id"] == str(sample_restaurant.id)


def test_submit_review_undelivered_order_rejected(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Review submission is rejected if the order is not yet DELIVERED."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)
    order.order_status = OrderStatus.PREPARING
    db_session.commit()

    payload = {
        "order_id": str(order.id),
        "restaurant_id": str(sample_restaurant.id),
        "rating": 4,
        "comment": "Food is still being prepared",
    }

    response = client.post("/api/reviews", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "delivered" in response.json()["detail"].lower()


def test_submit_duplicate_review_rejected(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Customer cannot review the same order twice."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)

    payload = {
        "order_id": str(order.id),
        "restaurant_id": str(sample_restaurant.id),
        "rating": 5,
        "comment": "First review",
    }
    res1 = client.post("/api/reviews", json=payload, headers=customer_headers)
    assert res1.status_code == 201

    res2 = client.post("/api/reviews", json=payload, headers=customer_headers)
    assert res2.status_code == 409
    assert "already been submitted" in res2.json()["detail"].lower()


def test_submit_review_invalid_rating(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Rating must be between 1 and 5."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)

    # Rating 0
    res_zero = client.post(
        "/api/reviews",
        json={"order_id": str(order.id), "restaurant_id": str(sample_restaurant.id), "rating": 0, "comment": "Bad"},
        headers=customer_headers,
    )
    assert res_zero.status_code == 422

    # Rating 6
    res_six = client.post(
        "/api/reviews",
        json={"order_id": str(order.id), "restaurant_id": str(sample_restaurant.id), "rating": 6, "comment": "Too good"},
        headers=customer_headers,
    )
    assert res_six.status_code == 422


def test_submit_review_idor_foreign_order(client, db_session, sample_customer, sample_restaurant, other_customer_headers):
    """Customer B cannot submit a review for Customer A's order."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)

    payload = {
        "order_id": str(order.id),
        "restaurant_id": str(sample_restaurant.id),
        "rating": 1,
        "comment": "I didn't order this",
    }

    response = client.post("/api/reviews", json=payload, headers=other_customer_headers)
    assert response.status_code == 403


def test_get_customer_reviews(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Customer can view their own previously submitted reviews."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)
    client.post(
        "/api/reviews",
        json={"order_id": str(order.id), "restaurant_id": str(sample_restaurant.id), "rating": 4, "comment": "Great meal"},
        headers=customer_headers,
    )

    response = client.get("/api/reviews/my-reviews", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["order_id"] == str(order.id)
    assert data[0]["rating"] == 4


def test_edit_review_success_and_idor(client, db_session, sample_customer, customer_headers, other_customer_headers, sample_restaurant):
    """Customer can edit their own review, but other customers cannot (IDOR)."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)
    res = client.post(
        "/api/reviews",
        json={"order_id": str(order.id), "restaurant_id": str(sample_restaurant.id), "rating": 3, "comment": "Average"},
        headers=customer_headers,
    )
    review_id = res.json()["id"]

    # Other customer tries to edit -> 403
    res_idor = client.put(
        f"/api/reviews/{review_id}",
        json={"rating": 1, "comment": "Hacked review"},
        headers=other_customer_headers,
    )
    assert res_idor.status_code == 403

    # Owner of review edits -> 200
    res_edit = client.put(
        f"/api/reviews/{review_id}",
        json={"rating": 4, "comment": "Actually turned out pretty good!"},
        headers=customer_headers,
    )
    assert res_edit.status_code == 200
    assert res_edit.json()["rating"] == 4
    assert res_edit.json()["comment"] == "Actually turned out pretty good!"


def test_delete_review_success_and_idor(client, db_session, sample_customer, customer_headers, other_customer_headers, sample_restaurant):
    """Customer can delete their own review, but other customers cannot."""
    order = create_delivered_order(db_session, sample_customer, sample_restaurant)
    res = client.post(
        "/api/reviews",
        json={"order_id": str(order.id), "restaurant_id": str(sample_restaurant.id), "rating": 2, "comment": "To delete"},
        headers=customer_headers,
    )
    review_id = res.json()["id"]

    # Other customer tries to delete -> 403
    res_idor = client.delete(f"/api/reviews/{review_id}", headers=other_customer_headers)
    assert res_idor.status_code == 403

    # Owner deletes -> 204
    res_del = client.delete(f"/api/reviews/{review_id}", headers=customer_headers)
    assert res_del.status_code == 204

    # Confirm it's gone
    my_reviews = client.get("/api/reviews/my-reviews", headers=customer_headers).json()
    assert not any(r["id"] == review_id for r in my_reviews)


def test_restaurant_review_summary_and_distribution(client, db_session, sample_customer, customer_headers, other_customer, other_customer_headers, sample_restaurant):
    """Public / customer can view restaurant review summary with average rating and rating breakdown."""
    order1 = create_delivered_order(db_session, sample_customer, sample_restaurant, amount=20.0)
    order2 = create_delivered_order(db_session, other_customer, sample_restaurant, amount=30.0)

    # Customer 1 gives 5 stars
    client.post(
        "/api/reviews",
        json={"order_id": str(order1.id), "restaurant_id": str(sample_restaurant.id), "rating": 5, "comment": "Loved it"},
        headers=customer_headers,
    )
    # Customer 2 gives 3 stars
    client.post(
        "/api/reviews",
        json={"order_id": str(order2.id), "restaurant_id": str(sample_restaurant.id), "rating": 3, "comment": "Decent"},
        headers=other_customer_headers,
    )

    response = client.get(f"/api/reviews/restaurant/{sample_restaurant.id}")
    assert response.status_code == 200
    summary = response.json()
    assert summary["restaurant_id"] == str(sample_restaurant.id)
    assert summary["total_reviews"] == 2
    assert summary["average_rating"] == 4.0
    assert summary["rating_distribution"]["5"] == 1
    assert summary["rating_distribution"]["3"] == 1
    assert summary["rating_distribution"]["1"] == 0
    assert len(summary["reviews"]) == 2
