"""Record BCB OLINDA Expectativas PIB Despesa de consumo da administração pública.

Revision ID: 0085_bcb_olinda_pib_despesa_adm
Revises: 0084_bcb_olinda_pib_despesa_fam
Create Date: 2026-09-21
"""

from alembic import op

revision = "0085_bcb_olinda_pib_despesa_adm"
down_revision = "0084_bcb_olinda_pib_despesa_fam"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.82' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.81' WHERE key = 'implementation_version'")
