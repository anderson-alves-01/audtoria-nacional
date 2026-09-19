"""Record complete official pipelines awaiting human validation.

Revision ID: 0017_official_complete
Revises: 0016_official_public_ingest
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0017_official_complete"
down_revision = "0016_official_public_ingest"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.14' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'REAL_DATA_PIPELINES_COMPLETE_AWAITING_HUMAN_VALIDATION' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
