"""Record BCB OLINDA Expectativas Investimento direto no pais.

Revision ID: 0079_bcb_olinda_investimento
Revises: 0078_bcb_olinda_taxa_desocup
Create Date: 2026-09-21
"""

from alembic import op


revision = "0079_bcb_olinda_investimento"
down_revision = "0078_bcb_olinda_taxa_desocup"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.76' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.75' WHERE key = 'implementation_version'")
