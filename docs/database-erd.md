# Campus Byte – Database Entity Relationship Diagram (ERD)

This document visualizes the complete normalized relational database schema for Campus Byte (Phase 2).

```mermaid
erDiagram
    USERS ||--o| RESTAURANTS : "owns (1:1 MVP)"
    USERS ||--o| DELIVERY_PARTNERS : "profile (1:1)"
    USERS ||--o{ ORDERS : "places as customer"
    USERS ||--o{ ORDER_STATUS_HISTORY : "changed_by"

    RESTAURANTS ||--o{ MENU_ITEMS : "offers"
    RESTAURANTS ||--o{ ORDERS : "receives"

    MENU_ITEMS ||--o{ ORDER_ITEMS : "snapshot in"

    ORDERS ||--|{ ORDER_ITEMS : "contains"
    ORDERS ||--o{ DELIVERY_ASSIGNMENTS : "dispatched via"
    ORDERS ||--o{ ORDER_STATUS_HISTORY : "audit history"

    DELIVERY_PARTNERS ||--o{ ORDERS : "assigned courier"
    DELIVERY_PARTNERS ||--o{ DELIVERY_ASSIGNMENTS : "accepts"

    USERS {
        uuid id PK
        string full_name
        string email UK
        string phone_number
        string password_hash
        string role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    RESTAURANTS {
        uuid id PK
        uuid owner_id FK,UK
        string name
        text description
        string address
        string contact_number
        string image_url
        boolean is_open
        timestamp created_at
        timestamp updated_at
    }

    MENU_ITEMS {
        uuid id PK
        uuid restaurant_id FK
        string name
        text description
        numeric price
        string category
        string image_url
        boolean is_available
        timestamp created_at
        timestamp updated_at
    }

    DELIVERY_PARTNERS {
        uuid id PK
        uuid user_id FK,UK
        string vehicle_type
        boolean is_available
        timestamp created_at
        timestamp updated_at
    }

    ORDERS {
        uuid id PK
        uuid customer_id FK
        uuid restaurant_id FK
        uuid delivery_partner_id FK
        string delivery_address
        numeric subtotal
        numeric delivery_fee
        numeric total_amount
        string payment_method
        string payment_status
        string order_status
        timestamp created_at
        timestamp updated_at
    }

    ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        uuid menu_item_id FK
        string item_name
        numeric unit_price
        integer quantity
        numeric total_price
    }

    DELIVERY_ASSIGNMENTS {
        uuid id PK
        uuid order_id FK
        uuid delivery_partner_id FK
        timestamp assigned_at
        timestamp picked_up_at
        timestamp delivered_at
        string delivery_status
    }

    ORDER_STATUS_HISTORY {
        uuid id PK
        uuid order_id FK
        string previous_status
        string new_status
        uuid changed_by FK
        timestamp created_at
    }
```

---

## Key Cardinalities & Constraints Summary

1. **User to Restaurant (1:1 MVP):**
   - Each restaurant is owned by one `RESTAURANT_OWNER` user.
   - Enforced by unique constraint `owner_id UNIQUE` on `restaurants`.
2. **User to Delivery Partner (1:1):**
   - Each courier profile belongs to one `DELIVERY_PARTNER` user.
   - Enforced by unique constraint `user_id UNIQUE` on `delivery_partners`.
3. **Restaurant to Menu Items (1:N):**
   - Cascading deletion: deleting a restaurant safely cleans up draft menu items if no orders exist.
4. **Order to Order Items (1:N):**
   - Strong composition. `order_items` stores historical snapshots of `item_name` and `unit_price`.
5. **Check Constraints:**
   - `menu_items.price > 0`
   - `order_items.quantity > 0`
   - `order_items.unit_price > 0`
   - `order_items.total_price > 0`
   - `orders.subtotal >= 0`, `orders.delivery_fee >= 0`, `orders.total_amount >= 0`
