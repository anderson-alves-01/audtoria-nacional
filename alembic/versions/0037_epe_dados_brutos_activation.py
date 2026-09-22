"""Record EPE Anuário Dados brutos UF-scoped activation.

Revision ID: 0037_epe_dados_brutos_activation
Revises: 0036_bcb_sgs_activation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0037_epe_dados_brutos_activation"
down_revision = "0036_bcb_sgs_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.34' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.33' WHERE key = 'implementation_version'")
