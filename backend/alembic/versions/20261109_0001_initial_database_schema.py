"""initial database schema

Revision ID: 20261109_0001
Revises: 
Create Date: 2026-11-09 16:30:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261109_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    # 2. restaurants
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("contact_number", sa.String(length=20), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_open", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", name="uq_restaurants_owner_id"),
    )
    op.create_index("ix_restaurants_name", "restaurants", ["name"], unique=False)
    op.create_index("ix_restaurants_is_open", "restaurants", ["is_open"], unique=False)
    op.create_index("ix_restaurants_owner_id", "restaurants", ["owner_id"], unique=True)

    # 3. menu_items
    op.create_table(
        "menu_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price > 0", name="check_menu_item_price_positive"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_menu_items_restaurant_id", "menu_items", ["restaurant_id"], unique=False)
    op.create_index("ix_menu_items_name", "menu_items", ["name"], unique=False)
    op.create_index("ix_menu_items_category", "menu_items", ["category"], unique=False)
    op.create_index("ix_menu_items_is_available", "menu_items", ["is_available"], unique=False)

    # 4. delivery_partners
    op.create_table(
        "delivery_partners",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("vehicle_type", sa.String(length=20), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_delivery_partners_user_id"),
    )
    op.create_index("ix_delivery_partners_user_id", "delivery_partners", ["user_id"], unique=True)
    op.create_index("ix_delivery_partners_is_available", "delivery_partners", ["is_available"], unique=False)

    # 5. orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_partner_id", sa.Uuid(), nullable=True),
        sa.Column("delivery_address", sa.String(length=255), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("delivery_fee", sa.Numeric(precision=10, scale=2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("total_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=False),
        sa.Column("payment_status", sa.String(length=20), nullable=False),
        sa.Column("order_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("subtotal >= 0", name="check_order_subtotal_non_negative"),
        sa.CheckConstraint("delivery_fee >= 0", name="check_order_delivery_fee_non_negative"),
        sa.CheckConstraint("total_amount >= 0", name="check_order_total_non_negative"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["delivery_partner_id"], ["delivery_partners.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"], unique=False)
    op.create_index("ix_orders_restaurant_id", "orders", ["restaurant_id"], unique=False)
    op.create_index("ix_orders_delivery_partner_id", "orders", ["delivery_partner_id"], unique=False)
    op.create_index("ix_orders_payment_status", "orders", ["payment_status"], unique=False)
    op.create_index("ix_orders_order_status", "orders", ["order_status"], unique=False)

    # 6. order_items
    op.create_table(
        "order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("menu_item_id", sa.Uuid(), nullable=False),
        sa.Column("item_name", sa.String(length=120), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
        sa.CheckConstraint("unit_price > 0", name="check_order_item_unit_price_positive"),
        sa.CheckConstraint("total_price > 0", name="check_order_item_total_price_positive"),
        sa.ForeignKeyConstraint(["menu_item_id"], ["menu_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)
    op.create_index("ix_order_items_menu_item_id", "order_items", ["menu_item_id"], unique=False)

    # 7. delivery_assignments
    op.create_table(
        "delivery_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_partner_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("picked_up_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["delivery_partner_id"], ["delivery_partners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_delivery_assignments_order_id", "delivery_assignments", ["order_id"], unique=False)
    op.create_index("ix_delivery_assignments_delivery_partner_id", "delivery_assignments", ["delivery_partner_id"], unique=False)
    op.create_index("ix_delivery_assignments_delivery_status", "delivery_assignments", ["delivery_status"], unique=False)

    # 8. order_status_history
    op.create_table(
        "order_status_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("previous_status", sa.String(length=30), nullable=True),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("changed_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_status_history_order_id", "order_status_history", ["order_id"], unique=False)
    op.create_index("ix_order_status_history_changed_by", "order_status_history", ["changed_by"], unique=False)


def downgrade() -> None:
    op.drop_table("order_status_history")
    op.drop_table("delivery_assignments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("delivery_partners")
    op.drop_table("menu_items")
    op.drop_table("restaurants")
    op.drop_table("users")

