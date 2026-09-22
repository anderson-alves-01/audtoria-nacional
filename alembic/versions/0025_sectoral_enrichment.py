"""Record F3 sectoral enrichment catalog shells.

Revision ID: 0025_sectoral_enrichment
Revises: 0024_municipal_cadastro_shells
Create Date: 2026-09-19
"""

from alembic import op

revision = "0025_sectoral_enrichment"
down_revision = "0024_municipal_cadastro_shells"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.22' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.21' WHERE key = 'implementation_version'")
