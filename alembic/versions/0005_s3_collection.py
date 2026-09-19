"""Sprint 3 collection schema. Seed is not applied here.

Revision ID: 0005_s3_collection
Revises: 0004_s2_validation
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0005_s3_collection"
down_revision = "0004_s2_validation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.3' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'S3_COLLECTION' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
