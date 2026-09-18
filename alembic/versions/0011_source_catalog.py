"""F3.0 synthetic source master registry schema.

Revision ID: 0011_source_catalog
Revises: 0010_alembic_hygiene
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0011_source_catalog"
down_revision = "0010_alembic_hygiene"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.9' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = 'F3_SOURCE_CATALOG_LOCAL' WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
