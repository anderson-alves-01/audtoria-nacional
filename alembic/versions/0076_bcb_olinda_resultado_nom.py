"""Record BCB OLINDA Expectativas Resultado nominal.

Revision ID: 0076_bcb_olinda_resultado_nom
Revises: 0075_bcb_olinda_resultado_conta
Create Date: 2026-09-21
"""

from alembic import op


revision = "0076_bcb_olinda_resultado_nom"
down_revision = "0075_bcb_olinda_resultado_conta"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.73' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.72' WHERE key = 'implementation_version'")
