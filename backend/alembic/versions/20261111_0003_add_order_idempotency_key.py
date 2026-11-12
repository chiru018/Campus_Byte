"""add idempotency_key to orders table

Revision ID: 20261111_0003
Revises: 20261111_0002
Create Date: 2026-11-11 15:58:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261111_0003"
down_revision: Union[str, None] = "20261111_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_orders_idempotency_key", "orders", ["idempotency_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_orders_idempotency_key", table_name="orders")
    op.drop_column("orders", "idempotency_key")

