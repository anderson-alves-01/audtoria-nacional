"""Record Tesouro monthly ITR/IPI-EXP/royalties allowlist activation.

Revision ID: 0054_tesouro_monthly_allowlist
Revises: 0053_state_es_go_ipi_cide
Create Date: 2026-09-20
"""

from alembic import op

revision = "0054_tesouro_monthly_allowlist"
down_revision = "0053_state_es_go_ipi_cide"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.51' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.50' WHERE key = 'implementation_version'")
