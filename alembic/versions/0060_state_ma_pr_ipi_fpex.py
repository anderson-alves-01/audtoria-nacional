"""Record MA/PR IPI-Exportação/FPEX and MS IPI/CIDE on approved state files.

Revision ID: 0060_state_ma_pr_ipi_fpex
Revises: 0059_state_pe_ba_mg_ipi
Create Date: 2026-09-21
"""

from alembic import op

revision = "0060_state_ma_pr_ipi_fpex"
down_revision = "0059_state_pe_ba_mg_ipi"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.57' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.56' WHERE key = 'implementation_version'")
