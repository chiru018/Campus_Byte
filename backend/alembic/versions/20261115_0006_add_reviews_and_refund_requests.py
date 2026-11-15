"""add reviews and refund requests tables

Revision ID: 20261115_0006
Revises: 20261112_0005
Create Date: 2026-11-15 14:55:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261115_0006"
down_revision: Union[str, None] = "20261112_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create reviews table
    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="check_review_rating_1_to_5"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", name="uq_reviews_order_id"),
    )
    op.create_index(op.f("ix_reviews_customer_id"), "reviews", ["customer_id"], unique=False)
    op.create_index(op.f("ix_reviews_restaurant_id"), "reviews", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_reviews_order_id"), "reviews", ["order_id"], unique=True)
    op.create_index(op.f("ix_reviews_rating"), "reviews", ["rating"], unique=False)

    # 2. Create refund_requests table
    op.create_table(
        "refund_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("issue_category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requested_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("approved_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("owner_response", sa.Text(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("requested_amount > 0", name="check_refund_requested_amount_positive"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refund_requests_order_id"), "refund_requests", ["order_id"], unique=False)
    op.create_index(op.f("ix_refund_requests_customer_id"), "refund_requests", ["customer_id"], unique=False)
    op.create_index(op.f("ix_refund_requests_restaurant_id"), "refund_requests", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_refund_requests_status"), "refund_requests", ["status"], unique=False)
    op.create_index(op.f("ix_refund_requests_issue_category"), "refund_requests", ["issue_category"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_refund_requests_issue_category"), table_name="refund_requests")
    op.drop_index(op.f("ix_refund_requests_status"), table_name="refund_requests")
    op.drop_index(op.f("ix_refund_requests_restaurant_id"), table_name="refund_requests")
    op.drop_index(op.f("ix_refund_requests_customer_id"), table_name="refund_requests")
    op.drop_index(op.f("ix_refund_requests_order_id"), table_name="refund_requests")
    op.drop_table("refund_requests")

    op.drop_index(op.f("ix_reviews_rating"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_order_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_restaurant_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_customer_id"), table_name="reviews")
    op.drop_table("reviews")

