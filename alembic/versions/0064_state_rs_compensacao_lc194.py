"""Record RS Compensação LC194 on MontaArquivo XLS.

Revision ID: 0064_state_rs_compensacao_lc194
Revises: 0063_ac_tr_icms_fundeb
Create Date: 2026-09-21
"""

from alembic import op

revision = "0064_state_rs_compensacao_lc194"
down_revision = "0063_ac_tr_icms_fundeb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.61' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.60' WHERE key = 'implementation_version'")
