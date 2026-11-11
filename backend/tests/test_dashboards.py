def test_dashboard_stats(client, sample_restaurant, sample_customer):
    """Test platform dashboard statistics summary."""
    # Add a menu item to the restaurant
    client.post(
        f"/api/restaurants/{sample_restaurant.id}/menu",
        json={"name": "Club Sandwich", "price": "6.50", "category": "Mains"},
    )

    response = client.get("/api/dashboards/stats")
    assert response.status_code == 200
    data = response.json()
    assert "restaurants" in data
    assert "menu_items" in data
    assert "users" in data
    assert data["restaurants"]["total"] >= 1
    assert data["menu_items"]["total"] >= 1
    assert data["users"]["total"] >= 2

