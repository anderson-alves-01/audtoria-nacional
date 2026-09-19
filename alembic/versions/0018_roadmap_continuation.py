"""Record official wave-1 lineage tables and roadmap continuation.

Revision ID: 0018_roadmap_continuation
Revises: 0017_official_complete
Create Date: 2026-09-19
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0018_roadmap_continuation"
down_revision = "0017_official_complete"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.15' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
