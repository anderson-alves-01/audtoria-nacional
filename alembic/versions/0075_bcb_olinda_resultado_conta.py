"""Record BCB OLINDA Expectativas Resultado primário + Conta corrente.

Revision ID: 0075_bcb_olinda_resultado_conta
Revises: 0074_bcb_olinda_divida_balanca
Create Date: 2026-09-21
"""

from alembic import op

revision = "0075_bcb_olinda_resultado_conta"
down_revision = "0074_bcb_olinda_divida_balanca"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.72' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.71' WHERE key = 'implementation_version'")
