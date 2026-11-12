"""add restaurant order processing fields and history notes

Revision ID: 20261112_0004
Revises: 20261111_0003
Create Date: 2026-11-12 15:24:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261112_0004"
down_revision: Union[str, None] = "20261111_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status timestamp and rejection columns to orders table
    op.add_column("orders", sa.Column("rejection_reason", sa.String(length=255), nullable=True))
    op.add_column("orders", sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("preparing_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("ready_for_pickup_at", sa.DateTime(timezone=True), nullable=True))

    # Add audit role and notes to order_status_history table
    op.add_column("order_status_history", sa.Column("changed_by_role", sa.String(length=30), nullable=True))
    op.add_column("order_status_history", sa.Column("notes", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("order_status_history", "notes")
    op.drop_column("order_status_history", "changed_by_role")
    op.drop_column("orders", "ready_for_pickup_at")
    op.drop_column("orders", "preparing_at")
    op.drop_column("orders", "rejected_at")
    op.drop_column("orders", "accepted_at")
    op.drop_column("orders", "rejection_reason")
