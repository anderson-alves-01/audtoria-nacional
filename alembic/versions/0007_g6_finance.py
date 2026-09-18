"""G6 finance schema. Seed is not applied here.

Revision ID: 0007_g6_finance
Revises: 0006_s4_pipeline
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0007_g6_finance"
down_revision = "0006_s4_pipeline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.5' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'G6_FINANCE' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
