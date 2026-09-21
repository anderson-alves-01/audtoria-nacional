"""Record BCB OLINDA Expectativas PIB Importação de bens e serviços.

Revision ID: 0087_bcb_olinda_pib_importacao
Revises: 0086_bcb_olinda_pib_exportacao
Create Date: 2026-09-21
"""

from alembic import op


revision = "0087_bcb_olinda_pib_importacao"
down_revision = "0086_bcb_olinda_pib_exportacao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.84' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.83' WHERE key = 'implementation_version'")
