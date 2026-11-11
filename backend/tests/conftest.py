import os
import sys
import uuid
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base
from app.db.session import get_db
from app.models import User, Restaurant, MenuItem, UserRole
from app.core.security import get_password_hash, create_access_token
from app.main import app

# Isolated in-memory SQLite engine for automated unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable Foreign Key and Check Constraints on SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh isolated database schema for each test function."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with get_db dependency overridden to the test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_owner(db_session) -> User:
    """Pre-created Restaurant Owner User fixture."""
    owner = User(
        id=uuid.uuid4(),
        full_name="Chef Gordon",
        email="chef.gordon@campusbyte.com",
        phone_number="+1234567890",
        password_hash=get_password_hash("ChefSecret123"),
        role=UserRole.RESTAURANT_OWNER,
        is_active=True,
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    return owner


@pytest.fixture
def sample_customer(db_session) -> User:
    """Pre-created Customer User fixture."""
    customer = User(
        id=uuid.uuid4(),
        full_name="Alice Student",
        email="alice.student@campusbyte.com",
        phone_number="+1987654321",
        password_hash=get_password_hash("AliceSecret123"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_restaurant(db_session, sample_owner) -> Restaurant:
    """Pre-created Restaurant fixture."""
    restaurant = Restaurant(
        id=uuid.uuid4(),
        owner_id=sample_owner.id,
        name="Campus Grill & Cafe",
        description="Fresh burgers, wraps, and coffee",
        address="Student Union Building, Floor 1",
        contact_number="+1555000111",
        image_url="https://images.unsplash.com/photo-campus-grill.jpg",
        is_open=True,
    )
    db_session.add(restaurant)
    db_session.commit()
    db_session.refresh(restaurant)
    return restaurant


@pytest.fixture
def owner_headers(sample_owner) -> dict:
    """Authorization header fixture for sample_owner."""
    token, _, _ = create_access_token(sample_owner.id, sample_owner.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(sample_customer) -> dict:
    """Authorization header fixture for sample_customer."""
    token, _, _ = create_access_token(sample_customer.id, sample_customer.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_owner(db_session) -> User:
    """Secondary Restaurant Owner for IDOR security tests."""
    owner = User(
        id=uuid.uuid4(),
        full_name="Chef Luigi",
        email="chef.luigi@campusbyte.com",
        phone_number="+1999888777",
        password_hash=get_password_hash("LuigiSecret123!"),
        role=UserRole.RESTAURANT_OWNER,
        is_active=True,
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    return owner


@pytest.fixture
def other_owner_headers(other_owner) -> dict:
    """Authorization header fixture for secondary owner."""
    token, _, _ = create_access_token(other_owner.id, other_owner.role.value)
    return {"Authorization": f"Bearer {token}"}


