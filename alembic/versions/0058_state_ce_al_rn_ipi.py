"""Record CE/AL/RN IPI activation on approved state transfer files.

Revision ID: 0058_state_ce_al_rn_ipi
Revises: 0057_tesouro_coint_cide_fex
Create Date: 2026-09-21
"""

from alembic import op

revision = "0058_state_ce_al_rn_ipi"
down_revision = "0057_tesouro_coint_cide_fex"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.55' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.54' WHERE key = 'implementation_version'")
