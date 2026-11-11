import uuid
from app.models import User, UserRole
from app.core.security import get_password_hash, create_access_token


def test_create_restaurant(client, db_session):
    """Test successful restaurant creation by an authenticated RESTAURANT_OWNER."""
    owner = User(
        id=uuid.uuid4(),
        full_name="Pizzeria Chef",
        email="chef.pizza@campus.edu",
        password_hash=get_password_hash("ChefPass123!"),
        role=UserRole.RESTAURANT_OWNER,
        is_active=True,
    )
    db_session.add(owner)
    db_session.commit()

    token, _, _ = create_access_token(owner.id, owner.role.value)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Pizza Corner",
        "description": "Authentic woodfired pizzas",
        "address": "Campus Center, Booth 4",
        "contact_number": "+1234567800",
        "image_url": "https://example.com/pizza.jpg",
        "is_open": True,
    }
    response = client.post("/api/restaurants", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Pizza Corner"
    assert data["owner_id"] == str(owner.id)
    assert data["is_open"] is True


def test_reject_restaurant_creation_by_customer(client, customer_headers):
    """Test creating a restaurant by a CUSTOMER role returns 403 Forbidden."""
    payload = {
        "name": "Student Kitchen",
        "address": "Dorm 4",
        "contact_number": "+1234567890",
    }
    response = client.post("/api/restaurants", json=payload, headers=customer_headers)
    assert response.status_code == 403


def test_reject_restaurant_creation_unauthenticated(client):
    """Test creating a restaurant without credentials returns 401 Unauthorized."""
    payload = {
        "name": "Ghost Kitchen",
        "address": "Nowhere",
        "contact_number": "+1000000000",
    }
    response = client.post("/api/restaurants", json=payload)
    assert response.status_code == 401


def test_reject_duplicate_restaurant_for_single_owner(client, sample_restaurant, owner_headers):
    """Test MVP 1:1 constraint (one restaurant per owner) returns 409 Conflict."""
    payload = {
        "name": "Second Branch Grill",
        "address": "South Gate",
        "contact_number": "+1555999888",
    }
    response = client.post("/api/restaurants", json=payload, headers=owner_headers)
    assert response.status_code == 409


def test_get_restaurants_list_and_search(client, sample_restaurant):
    """Test public listing of restaurants with pagination and search filter."""
    response = client.get("/api/restaurants?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(r["name"] == sample_restaurant.name for r in data["restaurants"])

    # Search keyword matching
    search_res = client.get("/api/restaurants?search=Grill")
    assert search_res.status_code == 200
    assert search_res.json()["total"] >= 1

    # Search keyword not matching
    no_match_res = client.get("/api/restaurants?search=NonExistentSushiPlace")
    assert no_match_res.status_code == 200
    assert no_match_res.json()["total"] == 0


def test_filter_restaurants_by_availability(client, sample_restaurant):
    """Test public filtering of restaurants by open/closed status."""
    res_open = client.get("/api/restaurants?is_open=true")
    assert res_open.status_code == 200
    assert any(r["id"] == str(sample_restaurant.id) for r in res_open.json()["restaurants"])

    res_closed = client.get("/api/restaurants?is_open=false")
    assert res_closed.status_code == 200
    assert not any(r["id"] == str(sample_restaurant.id) for r in res_closed.json()["restaurants"])


def test_get_restaurant_details(client, sample_restaurant):
    """Test retrieving public restaurant profile details by ID."""
    response = client.get(f"/api/restaurants/{sample_restaurant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_restaurant.id)
    assert data["name"] == sample_restaurant.name
    assert data["address"] == sample_restaurant.address


def test_get_my_restaurant(client, sample_restaurant, owner_headers):
    """Test retrieving the authenticated owner's restaurant via /my-restaurant."""
    response = client.get("/api/restaurants/my-restaurant", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_restaurant.id)
    assert data["name"] == sample_restaurant.name


def test_update_restaurant_by_owner(client, sample_restaurant, owner_headers):
    """Test updating restaurant details by the legitimate owner."""
    payload = {
        "name": "Campus Smokehouse & Grill",
        "description": "Authentic smoked meats and craft drinks",
    }
    response = client.put(
        f"/api/restaurants/{sample_restaurant.id}",
        json=payload,
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Campus Smokehouse & Grill"
    assert data["description"] == "Authentic smoked meats and craft drinks"


def test_reject_update_by_different_owner_idor(client, sample_restaurant, other_owner_headers):
    """Test IDOR prevention: Owner B cannot modify Owner A's restaurant (403 Forbidden)."""
    payload = {"name": "Hacked Restaurant"}
    response = client.put(
        f"/api/restaurants/{sample_restaurant.id}",
        json=payload,
        headers=other_owner_headers,
    )
    assert response.status_code == 403


def test_patch_restaurant_availability(client, sample_restaurant, owner_headers):
    """Test toggling restaurant availability by legitimate owner."""
    response = client.patch(
        f"/api/restaurants/{sample_restaurant.id}/availability",
        json={"is_open": False},
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_open"] is False

    # Toggle back to open
    res_reopen = client.patch(
        f"/api/restaurants/{sample_restaurant.id}/availability",
        json={"is_open": True},
        headers=owner_headers,
    )
    assert res_reopen.status_code == 200
    assert res_reopen.json()["is_open"] is True


def test_get_restaurant_stats(client, sample_restaurant, owner_headers):
    """Test retrieving restaurant stats for dashboard."""
    response = client.get(
        f"/api/restaurants/{sample_restaurant.id}/stats",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_name"] == sample_restaurant.name
    assert "total_menu_items" in data
    assert "profile_completion_percentage" in data


def test_delete_restaurant(client, sample_restaurant, owner_headers):
    """Test deleting an empty restaurant with no historical orders."""
    response = client.delete(
        f"/api/restaurants/{sample_restaurant.id}",
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_deactivated"] is False

    # Confirm it no longer exists
    get_res = client.get(f"/api/restaurants/{sample_restaurant.id}")
    assert get_res.status_code == 404
