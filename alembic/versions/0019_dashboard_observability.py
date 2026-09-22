"""Record dashboard observability and regulatory LC214 slice.

Revision ID: 0019_dashboard_observability
Revises: 0018_roadmap_continuation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0019_dashboard_observability"
down_revision = "0018_roadmap_continuation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.16' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.15' WHERE key = 'implementation_version'")
