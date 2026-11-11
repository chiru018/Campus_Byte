import uuid
from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.models import (
    User,
    Restaurant,
    MenuItem,
    DeliveryPartner,
    Order,
    OrderItem,
    DeliveryAssignment,
    OrderStatusHistory,
    UserRole,
    VehicleType,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    DeliveryStatus,
)
from app.core.security import get_password_hash


def test_database_connection(db_session):
    """Test raw SQL execution verifying basic connectivity."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_model_creation_and_relationships(db_session):
    """Test creation of all 8 core entities and verify foreign key relationships."""
    # 1. User: Customer
    customer = User(
        id=uuid.uuid4(),
        full_name="Bob Student",
        email="bob@campus.edu",
        password_hash=get_password_hash("BobPassword123"),
        role=UserRole.CUSTOMER,
    )
    # 2. User: Owner
    owner = User(
        id=uuid.uuid4(),
        full_name="Mama Rosa",
        email="rosa@campus.edu",
        password_hash=get_password_hash("RosaPassword123"),
        role=UserRole.RESTAURANT_OWNER,
    )
    # 3. User: Delivery Partner
    courier_user = User(
        id=uuid.uuid4(),
        full_name="Dave Rider",
        email="dave@campus.edu",
        password_hash=get_password_hash("DavePassword123"),
        role=UserRole.DELIVERY_PARTNER,
    )
    db_session.add_all([customer, owner, courier_user])
    db_session.commit()

    # 4. DeliveryPartner Profile
    courier = DeliveryPartner(
        id=uuid.uuid4(),
        user_id=courier_user.id,
        vehicle_type=VehicleType.BICYCLE,
        is_available=True,
    )
    db_session.add(courier)

    # 5. Restaurant
    restaurant = Restaurant(
        id=uuid.uuid4(),
        owner_id=owner.id,
        name="Mama Rosa Pizzeria",
        address="North Dorm Quad #3",
        contact_number="+1555123456",
        is_open=True,
    )
    db_session.add(restaurant)
    db_session.commit()

    # 6. MenuItem
    item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=restaurant.id,
        name="Margherita Slice",
        description="Tomato sauce, fresh mozzarella, basil",
        price=Decimal("4.50"),
        category="Pizza",
        is_available=True,
    )
    db_session.add(item)
    db_session.commit()

    # 7. Order
    order = Order(
        id=uuid.uuid4(),
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        delivery_partner_id=courier.id,
        delivery_address="Hall B, Room 304",
        subtotal=Decimal("9.00"),
        delivery_fee=Decimal("1.50"),
        total_amount=Decimal("10.50"),
        payment_method=PaymentMethod.CASH_ON_DELIVERY,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
    )
    db_session.add(order)
    db_session.commit()

    # 8. OrderItem
    order_item = OrderItem(
        id=uuid.uuid4(),
        order_id=order.id,
        menu_item_id=item.id,
        item_name=item.name,
        unit_price=item.price,
        quantity=2,
        total_price=Decimal("9.00"),
    )
    # 9. DeliveryAssignment
    assignment = DeliveryAssignment(
        id=uuid.uuid4(),
        order_id=order.id,
        delivery_partner_id=courier.id,
        delivery_status=DeliveryStatus.ASSIGNED,
    )
    # 10. OrderStatusHistory
    history = OrderStatusHistory(
        id=uuid.uuid4(),
        order_id=order.id,
        previous_status=None,
        new_status=OrderStatus.PENDING.value,
        changed_by=customer.id,
    )
    db_session.add_all([order_item, assignment, history])
    db_session.commit()

    # Verify relationships via queries
    loaded_order = db_session.get(Order, order.id)
    assert loaded_order is not None
    assert loaded_order.customer.email == "bob@campus.edu"
    assert loaded_order.restaurant.name == "Mama Rosa Pizzeria"
    assert loaded_order.delivery_partner.user.email == "dave@campus.edu"
    assert len(loaded_order.order_items) == 1
    assert loaded_order.order_items[0].item_name == "Margherita Slice"
    assert len(loaded_order.delivery_assignments) == 1
    assert len(loaded_order.status_history) == 1


def test_unique_email_constraint(db_session):
    """Test that duplicate email addresses are rejected by database constraint."""
    u1 = User(
        id=uuid.uuid4(),
        full_name="User One",
        email="duplicate@campus.edu",
        password_hash="hash1",
        role=UserRole.CUSTOMER,
    )
    db_session.add(u1)
    db_session.commit()

    u2 = User(
        id=uuid.uuid4(),
        full_name="User Two",
        email="duplicate@campus.edu",
        password_hash="hash2",
        role=UserRole.CUSTOMER,
    )
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_menu_item_positive_price_constraint(db_session, sample_restaurant):
    """Test check constraint enforcing price > 0."""
    invalid_item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=sample_restaurant.id,
        name="Free / Negative Drink",
        price=Decimal("-2.50"),
        category="Beverages",
    )
    db_session.add(invalid_item)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_order_item_positive_quantity_constraint(db_session, sample_restaurant, sample_customer):
    """Test check constraint enforcing quantity > 0."""
    item = MenuItem(
        id=uuid.uuid4(),
        restaurant_id=sample_restaurant.id,
        name="Sandwich",
        price=Decimal("5.00"),
        category="Mains",
    )
    db_session.add(item)
    db_session.commit()

    order = Order(
        id=uuid.uuid4(),
        customer_id=sample_customer.id,
        restaurant_id=sample_restaurant.id,
        delivery_address="Library 2nd Floor",
        subtotal=Decimal("5.00"),
        delivery_fee=Decimal("1.00"),
        total_amount=Decimal("6.00"),
    )
    db_session.add(order)
    db_session.commit()

    invalid_order_item = OrderItem(
        id=uuid.uuid4(),
        order_id=order.id,
        menu_item_id=item.id,
        item_name="Sandwich",
        unit_price=Decimal("5.00"),
        quantity=0,  # Invalid: must be > 0
        total_price=Decimal("0.00"),
    )
    db_session.add(invalid_order_item)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

