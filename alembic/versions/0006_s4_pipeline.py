"""Sprint 4 synthetic ISS pipeline tables.

Revision ID: 0006_s4_pipeline
Revises: 0005_s3_collection
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0006_s4_pipeline"
down_revision = "0005_s3_collection"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.4' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'S4_SYNTHETIC_DATA' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
