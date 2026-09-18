"""F0 schema metadata.

Revision ID: 0001_f0_schema_meta
Revises:
Create Date: 2026-09-18
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_f0_schema_meta"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schema_meta",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.String(length=128), nullable=False),
    )
    op.execute(
        "INSERT INTO schema_meta (key, value) VALUES "
        "('implementation_version', '0.3.1'),"
        "('spec_version', '0.3.0'),"
        "('release_stage', 'F0_FOUNDATION')"
    )


def downgrade() -> None:
    op.drop_table("schema_meta")
