import uuid
from decimal import Decimal
import pytest
from app.models import Order, OrderItem, MenuItem
from app.models.enums import OrderStatus, PaymentStatus, PaymentMethod


def seed_customer_orders(db_session, customer, restaurant):
    """Seed multiple realistic orders for insights testing."""
    burger = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=restaurant.id,
        name="Classic Cheeseburger",
        category="BURGERS",
        price=Decimal("12.00"),
        is_available=True,
    )
    fries = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=restaurant.id,
        name="Curly Fries",
        category="SIDES",
        price=Decimal("5.00"),
        is_available=True,
    )
    db_session.add_all([burger, fries])
    db_session.commit()

    # Order 1: 1 Burger + 1 Fries = $17.00
    order1 = Order(
        id=uuid.uuid4(),
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        order_status=OrderStatus.DELIVERED,
        total_amount=Decimal("17.00"),
        subtotal=Decimal("17.00"),
        delivery_fee=Decimal("0.00"),
        delivery_address="Hostel 2, Room 10",
        payment_method=PaymentMethod.CASH_ON_DELIVERY,
        payment_status=PaymentStatus.PAID,
    )
    db_session.add(order1)
    db_session.commit()

    item1 = OrderItem(
        id=uuid.uuid4(),
        order_id=order1.id,
        menu_item_id=burger.id,
        item_name=burger.name,
        quantity=1,
        unit_price=Decimal("12.00"),
        total_price=Decimal("12.00"),
    )
    item2 = OrderItem(
        id=uuid.uuid4(),
        order_id=order1.id,
        menu_item_id=fries.id,
        item_name=fries.name,
        quantity=1,
        unit_price=Decimal("5.00"),
        total_price=Decimal("5.00"),
    )
    db_session.add_all([item1, item2])

    # Order 2: 2 Burgers = $24.00
    order2 = Order(
        id=uuid.uuid4(),
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        order_status=OrderStatus.DELIVERED,
        total_amount=Decimal("24.00"),
        subtotal=Decimal("24.00"),
        delivery_fee=Decimal("0.00"),
        delivery_address="Hostel 2, Room 10",
        payment_method=PaymentMethod.CASH_ON_DELIVERY,
        payment_status=PaymentStatus.PAID,
    )
    db_session.add(order2)
    db_session.commit()

    item3 = OrderItem(
        id=uuid.uuid4(),
        order_id=order2.id,
        menu_item_id=burger.id,
        item_name=burger.name,
        quantity=2,
        unit_price=Decimal("12.00"),
        total_price=Decimal("24.00"),
    )
    db_session.add(item3)
    db_session.commit()

    return [order1, order2]


def test_customer_spending_summary_zero_state(client, customer_headers):
    """Customer with no orders gets zeroed spending metrics cleanly."""
    response = client.get("/api/insights/summary", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_spent"]) == 0.0
    assert data["total_orders"] == 0
    assert float(data["average_order_value"]) == 0.0
    assert data["monthly_spending"] == []


def test_customer_spending_summary_with_orders(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Customer spending summary accurately aggregates orders."""
    seed_customer_orders(db_session, sample_customer, sample_restaurant)

    response = client.get("/api/insights/summary", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_spent"]) == 41.0  # 17.0 + 24.0
    assert data["total_orders"] == 2
    assert float(data["average_order_value"]) == 20.5  # 41 / 2
    assert len(data["monthly_spending"]) >= 1


def test_customer_ordering_patterns(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Ordering patterns correctly identify top dishes, favourite restaurant, and categories."""
    seed_customer_orders(db_session, sample_customer, sample_restaurant)

    response = client.get("/api/insights/patterns", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["top_dishes"][0]["dish_name"] == "Classic Cheeseburger"
    assert data["top_dishes"][0]["total_quantity"] == 3  # 1 in order1 + 2 in order2
    assert data["favourite_restaurants"][0]["restaurant_name"] == sample_restaurant.name
    assert any(c["category"] == "BURGERS" for c in data["top_categories"])


def test_customer_recommendations(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """Recommendations service returns active menu suggestions."""
    seed_customer_orders(db_session, sample_customer, sample_restaurant)

    response = client.get("/api/insights/recommendations", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1
    assert "reason" in data["recommendations"][0]
    assert data["recommendations"][0]["dish_name"] != ""


def test_customer_ai_narrative(client, db_session, sample_customer, customer_headers, sample_restaurant):
    """AI Narrative returns a structured summary with fallback resilience."""
    seed_customer_orders(db_session, sample_customer, sample_restaurant)

    response = client.get("/api/insights/ai-summary", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert "narrative" in data
    assert len(data["narrative"]) > 0
    assert isinstance(data["key_highlights"], list)
    assert data["source"] in ["gemini", "rule_based"]


def test_insights_customer_isolation(
    client,
    db_session,
    sample_customer,
    customer_headers,
    other_customer,
    other_customer_headers,
    sample_restaurant,
):
    """Customer A's spending is completely isolated from Customer B's."""
    seed_customer_orders(db_session, sample_customer, sample_restaurant)

    # Customer A should see $41 spent
    res_a = client.get("/api/insights/summary", headers=customer_headers)
    assert res_a.status_code == 200
    assert float(res_a.json()["total_spent"]) == 41.0

    # Customer B has 0 orders and should see $0 spent
    res_b = client.get("/api/insights/summary", headers=other_customer_headers)
    assert res_b.status_code == 200
    assert float(res_b.json()["total_spent"]) == 0.0
