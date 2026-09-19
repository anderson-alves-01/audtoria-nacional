"""Record F3 controlled backfill safety for FPM/RREO/DCA.

Revision ID: 0026_controlled_backfill
Revises: 0025_sectoral_enrichment
Create Date: 2026-09-19
"""

from alembic import op

revision = "0026_controlled_backfill"
down_revision = "0025_sectoral_enrichment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.23' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.22' WHERE key = 'implementation_version'")
