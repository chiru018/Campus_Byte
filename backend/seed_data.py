"""
Campus Byte - Database Seed Script
Populates demo users (Customer, Restaurant Owner, Delivery Partner),
restaurants, and menu items for seamless full-stack testing.

Usage:
    python seed_data.py
"""

import sys
import os
import uuid

# Ensure backend root is in python sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app.models  # noqa: F401
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.menu_item import MenuItem
from app.models.delivery_partner import DeliveryPartner
from app.models.enums import UserRole, FoodCategory, VehicleType, PartnerAvailability
from app.core.security import get_password_hash


def seed_database():
    print("=" * 60)
    print("  Campus Byte - Seeding Initial Database Records")
    print("=" * 60)

    # Ensure all tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Customer User
        customer = db.query(User).filter(User.email == "student@campusbyte.com").first()
        if not customer:
            customer = User(
                id=uuid.uuid4(),
                full_name="Alex Student",
                email="student@campusbyte.com",
                phone_number="+15551234567",
                password_hash=get_password_hash("Student123"),
                role=UserRole.CUSTOMER,
                is_active=True,
            )
            db.add(customer)
            db.flush()
            print(" Created Customer: student@campusbyte.com / Student123")
        else:
            print(" Customer already exists: student@campusbyte.com")

        # 2. Restaurant Owner User
        owner = db.query(User).filter(User.email == "owner@campusbyte.com").first()
        if not owner:
            owner = User(
                id=uuid.uuid4(),
                full_name="Chef Marco",
                email="owner@campusbyte.com",
                phone_number="+15559876543",
                password_hash=get_password_hash("Owner123"),
                role=UserRole.RESTAURANT_OWNER,
                is_active=True,
            )
            db.add(owner)
            db.flush()
            print(" Created Restaurant Owner: owner@campusbyte.com / Owner123")
        else:
            print(" Restaurant Owner already exists: owner@campusbyte.com")

        # 3. Delivery Partner User
        courier_user = db.query(User).filter(User.email == "courier@campusbyte.com").first()
        if not courier_user:
            courier_user = User(
                id=uuid.uuid4(),
                full_name="Sam Swift",
                email="courier@campusbyte.com",
                phone_number="+15554567890",
                password_hash=get_password_hash("Courier123"),
                role=UserRole.DELIVERY_PARTNER,
                is_active=True,
            )
            db.add(courier_user)
            db.flush()

            courier_profile = DeliveryPartner(
                user_id=courier_user.id,
                vehicle_type=VehicleType.BIKE,
                vehicle_registration_number="CAMPUS-RUN-01",
                availability_status=PartnerAvailability.AVAILABLE,
                is_available=True,
            )
            db.add(courier_profile)
            db.flush()
            print(" Created Delivery Partner: courier@campusbyte.com / Courier123")
        else:
            print(" Delivery Partner already exists: courier@campusbyte.com")

        # 4. Restaurant: Campus Spice Kitchen
        restaurant = db.query(Restaurant).filter(Restaurant.owner_id == owner.id).first()
        if not restaurant:
            restaurant = Restaurant(
                id=uuid.uuid4(),
                owner_id=owner.id,
                name="Campus Spice Kitchen",
                description="Authentic biryanis, rolls, and curries right in the Student Activity Center.",
                address="Student Activity Center (SAC), Ground Floor",
                contact_number="+15559876543",
                image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
                is_open=True,
            )
            db.add(restaurant)
            db.flush()
            print(" Created Restaurant: Campus Spice Kitchen")
        else:
            print(f" Restaurant already exists: {restaurant.name}")

        # 5. Menu Items for Campus Spice Kitchen
        menu_items_data = [
            {
                "name": "Hyderabadi Chicken Biryani",
                "description": "Fragrant basmati rice layered with spiced marinated chicken and saffron.",
                "price": 8.99,
                "category": FoodCategory.BIRYANI,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&q=80",
            },
            {
                "name": "Paneer Tikka Roll",
                "description": "Char-grilled cottage cheese cubes wrapped in warm rumali roti with mint chutney.",
                "price": 5.49,
                "category": FoodCategory.NORTH_INDIAN,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500&q=80",
            },
            {
                "name": "Crispy Veggie Burger",
                "description": "Spicy spiced potato and pea patty with fresh lettuce, tomato, and chipotle mayo.",
                "price": 4.99,
                "category": FoodCategory.BURGERS,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&q=80",
            },
            {
                "name": "Classic Margherita Pizza",
                "description": "Thin crust with San Marzano tomato sauce, fresh mozzarella, and basil leaves.",
                "price": 7.99,
                "category": FoodCategory.PIZZA,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&q=80",
            },
            {
                "name": "Masala Chai",
                "description": "Freshly brewed Indian spiced tea with cardamom, ginger, and milk.",
                "price": 1.99,
                "category": FoodCategory.BEVERAGES,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&q=80",
            },
            {
                "name": "Cold Coffee with Vanilla Ice Cream",
                "description": "Rich blended espresso milk topped with a scoop of Madagascar vanilla.",
                "price": 3.49,
                "category": FoodCategory.BEVERAGES,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=500&q=80",
            },
        ]

        for item_data in menu_items_data:
            existing = (
                db.query(MenuItem)
                .filter(
                    MenuItem.restaurant_id == restaurant.id,
                    MenuItem.name == item_data["name"],
                )
                .first()
            )
            if not existing:
                item = MenuItem(
                    id=uuid.uuid4(),
                    restaurant_id=restaurant.id,
                    name=item_data["name"],
                    description=item_data["description"],
                    price=item_data["price"],
                    category=item_data["category"],
                    is_available=item_data["is_available"],
                    image_url=item_data["image_url"],
                )
                db.add(item)
                print(f" Added Menu Item: {item_data['name']} (${item_data['price']})")

        db.commit()
        print("\n [SUCCESS] Seed data completed successfully!")
        print("\nDemo Credentials:")
        print("  Customer:         student@campusbyte.com   / Student123")
        print("  Restaurant Owner: owner@campusbyte.com     / Owner123")
        print("  Delivery Partner: courier@campusbyte.com   / Courier123")
        print("=" * 60)
    except Exception as exc:
        db.rollback()
        print(f"\n [ERROR] Seeding failed: {exc}")
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
