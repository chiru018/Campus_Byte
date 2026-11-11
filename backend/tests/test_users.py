import uuid


def test_create_user(client):
    """Test successful user creation through API."""
    payload = {
        "full_name": "John Doe",
        "email": "john.doe@campus.edu",
        "phone_number": "+1234567890",
        "role": "CUSTOMER",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["email"] == "john.doe@campus.edu"
    assert data["role"] == "CUSTOMER"
    assert "id" in data
    # Security requirement: password_hash must NEVER be exposed
    assert "password_hash" not in data
    assert "password" not in data


def test_reject_duplicate_user_email(client):
    """Test that registering an existing email returns 409 Conflict."""
    payload = {
        "full_name": "First User",
        "email": "unique@campus.edu",
        "role": "CUSTOMER",
        "password": "Password123",
    }
    res1 = client.post("/api/users", json=payload)
    assert res1.status_code == 201

    # Attempt to create with same email
    res2 = client.post("/api/users", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_get_user_by_id(client, sample_customer):
    """Test retrieving user details by ID."""
    response = client.get(f"/api/users/{sample_customer.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_customer.id)
    assert data["email"] == sample_customer.email
    assert "password_hash" not in data


def test_get_nonexistent_user(client):
    """Test retrieving an invalid user ID returns 404."""
    random_id = uuid.uuid4()
    response = client.get(f"/api/users/{random_id}")
    assert response.status_code == 404


def test_list_users(client, sample_customer, sample_owner):
    """Test listing users with pagination."""
    response = client.get("/api/users?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["users"]) >= 2
    for user in data["users"]:
        assert "password_hash" not in user

