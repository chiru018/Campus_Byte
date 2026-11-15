"""add delivery partner availability, assignment tracking and order delivery fields

Revision ID: 20261112_0005
Revises: 20261112_0004
Create Date: 2026-11-12 15:52:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261112_0005"
down_revision: Union[str, None] = "20261112_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    
    def has_col(table, col):
        return col in [c["name"] for c in insp.get_columns(table)]

    # 1. Update delivery_partners table
    if not has_col("delivery_partners", "vehicle_registration_number"):
        op.add_column(
            "delivery_partners",
            sa.Column("vehicle_registration_number", sa.String(length=50), nullable=True),
        )
    if not has_col("delivery_partners", "availability_status"):
        op.add_column(
            "delivery_partners",
            sa.Column(
                "availability_status",
                sa.String(length=20),
                server_default="AVAILABLE",
                nullable=False,
            ),
        )
        op.create_index(
            "ix_delivery_partners_availability_status",
            "delivery_partners",
            ["availability_status"],
            unique=False,
        )

    # 2. Update delivery_assignments table
    if not has_col("delivery_assignments", "started_delivery_at"):
        op.add_column(
            "delivery_assignments",
            sa.Column("started_delivery_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not has_col("delivery_assignments", "completed_at"):
        op.add_column(
            "delivery_assignments",
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not has_col("delivery_assignments", "created_at"):
        op.add_column(
            "delivery_assignments",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not has_col("delivery_assignments", "updated_at"):
        op.add_column(
            "delivery_assignments",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    # 3. Update orders table
    if not has_col("orders", "picked_up_at"):
        op.add_column(
            "orders",
            sa.Column("picked_up_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not has_col("orders", "out_for_delivery_at"):
        op.add_column(
            "orders",
            sa.Column("out_for_delivery_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not has_col("orders", "delivered_at"):
        op.add_column(
            "orders",
            sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not has_col("orders", "cod_collected"):
        op.add_column(
            "orders",
            sa.Column(
                "cod_collected",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
        )
    if not has_col("orders", "cod_collected_at"):
        op.add_column(
            "orders",
            sa.Column("cod_collected_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not has_col("orders", "cod_collected_by"):
        op.add_column(
            "orders",
            sa.Column("cod_collected_by", sa.Uuid(), nullable=True),
        )
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_orders_cod_collected_by",
            "orders",
            "users",
            ["cod_collected_by"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_orders_cod_collected_by", "orders", type_="foreignkey")
    op.drop_column("orders", "cod_collected_by")
    op.drop_column("orders", "cod_collected_at")
    op.drop_column("orders", "cod_collected")
    op.drop_column("orders", "delivered_at")
    op.drop_column("orders", "out_for_delivery_at")
    op.drop_column("orders", "picked_up_at")

    op.drop_column("delivery_assignments", "updated_at")
    op.drop_column("delivery_assignments", "created_at")
    op.drop_column("delivery_assignments", "completed_at")
    op.drop_column("delivery_assignments", "started_delivery_at")

    op.drop_index("ix_delivery_partners_availability_status", "delivery_partners")
    op.drop_column("delivery_partners", "availability_status")
    op.drop_column("delivery_partners", "vehicle_registration_number")

