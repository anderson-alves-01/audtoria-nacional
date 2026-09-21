"""Record ES IPI/CIDE and GO IPI Economia activation.

Revision ID: 0053_state_es_go_ipi_cide
Revises: 0052_state_go_icms_economia
Create Date: 2026-09-20
"""

from alembic import op

revision = "0053_state_es_go_ipi_cide"
down_revision = "0052_state_go_icms_economia"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.50' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.49' WHERE key = 'implementation_version'")
