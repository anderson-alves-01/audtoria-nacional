"""Record AL/PR state royalties on approved transfer files.

Revision ID: 0061_state_al_pr_royalty
Revises: 0060_state_ma_pr_ipi_fpex
Create Date: 2026-09-21
"""

from alembic import op

revision = "0061_state_al_pr_royalty"
down_revision = "0060_state_ma_pr_ipi_fpex"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.58' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.57' WHERE key = 'implementation_version'")
