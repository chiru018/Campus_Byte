import uuid
from app.models import User, UserRole
from app.core.security import get_password_hash


def test_create_restaurant(client, db_session):
    """Test successful restaurant creation."""
    owner = User(
        id=uuid.uuid4(),
        full_name="Pizzeria Chef",
        email="chef.pizza@campus.edu",
        password_hash=get_password_hash("ChefPass123"),
        role=UserRole.RESTAURANT_OWNER,
    )
    db_session.add(owner)
    db_session.commit()

    payload = {
        "owner_id": str(owner.id),
        "name": "Pizza Corner",
        "description": "Authentic woodfired pizzas",
        "address": "Campus Center, Booth 4",
        "contact_number": "+1234567800",
        "image_url": "https://example.com/pizza.jpg",
        "is_open": True,
    }
    response = client.post("/api/restaurants", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Pizza Corner"
    assert data["owner_id"] == str(owner.id)
    assert data["is_open"] is True


def test_reject_restaurant_with_nonexistent_owner(client):
    """Test creating a restaurant with non-existent owner ID returns 404."""
    payload = {
        "owner_id": str(uuid.uuid4()),
        "name": "Ghost Kitchen",
        "address": "Nowhere",
        "contact_number": "+1000000000",
    }
    response = client.post("/api/restaurants", json=payload)
    assert response.status_code == 404


def test_reject_restaurant_with_invalid_role(client, sample_customer):
    """Test creating restaurant where owner has CUSTOMER role returns 400."""
    payload = {
        "owner_id": str(sample_customer.id),
        "name": "Student Kitchen",
        "address": "Dorm 4",
        "contact_number": "+1234567890",
    }
    response = client.post("/api/restaurants", json=payload)
    assert response.status_code == 400
    assert "must have role 'RESTAURANT_OWNER'" in response.json()["detail"]


def test_reject_duplicate_restaurant_for_single_owner(client, sample_restaurant, sample_owner):
    """Test MVP 1:1 constraint (one restaurant per owner) returns 409."""
    payload = {
        "owner_id": str(sample_owner.id),
        "name": "Second Branch Grill",
        "address": "South Gate",
        "contact_number": "+1555999888",
    }
    response = client.post("/api/restaurants", json=payload)
    assert response.status_code == 409


def test_get_restaurants_list_and_search(client, sample_restaurant):
    """Test listing restaurants with pagination and search filter."""
    response = client.get("/api/restaurants?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(r["name"] == sample_restaurant.name for r in data["restaurants"])

    # Search by keyword matching
    search_res = client.get("/api/restaurants?search=Grill")
    assert search_res.status_code == 200
    assert search_res.json()["total"] >= 1

    # Search keyword not matching
    no_match_res = client.get("/api/restaurants?search=NonExistentSushiPlace")
    assert no_match_res.status_code == 200
    assert no_match_res.json()["total"] == 0


def test_filter_restaurants_by_availability(client, sample_restaurant, db_session):
    """Test filtering restaurants by is_open status."""
    # Open filter
    res_open = client.get("/api/restaurants?is_open=true")
    assert res_open.status_code == 200
    assert any(r["id"] == str(sample_restaurant.id) for r in res_open.json()["restaurants"])

    # Closed filter
    res_closed = client.get("/api/restaurants?is_open=false")
    assert res_closed.status_code == 200
    assert not any(r["id"] == str(sample_restaurant.id) for r in res_closed.json()["restaurants"])


def test_get_restaurant_details(client, sample_restaurant):
    """Test retrieving restaurant by ID."""
    response = client.get(f"/api/restaurants/{sample_restaurant.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_restaurant.name


def test_update_restaurant(client, sample_restaurant):
    """Test updating restaurant information."""
    payload = {
        "name": "Campus Gourmet Bistro",
        "address": "Student Union Building, Floor 2",
    }
    response = client.put(f"/api/restaurants/{sample_restaurant.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Campus Gourmet Bistro"
    assert data["address"] == "Student Union Building, Floor 2"


def test_patch_restaurant_availability(client, sample_restaurant):
    """Test toggling restaurant availability."""
    response = client.patch(
        f"/api/restaurants/{sample_restaurant.id}/availability",
        json={"is_open": False},
    )
    assert response.status_code == 200
    assert response.json()["is_open"] is False


def test_delete_restaurant(client, sample_restaurant):
    """Test safe restaurant deletion."""
    response = client.delete(f"/api/restaurants/{sample_restaurant.id}")
    assert response.status_code == 200
    # Verify it is deleted
    check_res = client.get(f"/api/restaurants/{sample_restaurant.id}")
    assert check_res.status_code == 404
