"""Mark a user access as active. Existing rows stay active.

Revision ID: 0106_user_access_active
Revises: 0105_tax_better_source_config
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0106_user_access_active"
down_revision = "0105_tax_better_source_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("users", "active")
