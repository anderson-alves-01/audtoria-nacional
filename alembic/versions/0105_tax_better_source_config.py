"""Operator configuration for a Tax Better source. No organ credentials are stored.

Revision ID: 0105_tax_better_source_config
Revises: 0104_tax_better_vision
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0105_tax_better_source_config"
down_revision = "0104_tax_better_vision"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tax_better_source_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "territory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("territories.id"),
            nullable=False,
        ),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=8), nullable=False),
        sa.Column("field_map", postgresql.JSONB(), nullable=False),
        sa.Column("endpoint", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("secret_name", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "territory_id",
            "source_id",
            name="uq_tax_better_source_config",
        ),
    )


def downgrade() -> None:
    op.drop_table("tax_better_source_configs")
