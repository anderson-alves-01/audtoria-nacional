"""Record BCB OLINDA Expectativas PIB Exportação de bens e serviços.

Revision ID: 0086_bcb_olinda_pib_exportacao
Revises: 0085_bcb_olinda_pib_despesa_adm
Create Date: 2026-09-21
"""

from alembic import op

revision = "0086_bcb_olinda_pib_exportacao"
down_revision = "0085_bcb_olinda_pib_despesa_adm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.83' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.82' WHERE key = 'implementation_version'")
