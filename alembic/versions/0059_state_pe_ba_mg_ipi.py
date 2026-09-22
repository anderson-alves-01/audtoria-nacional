"""Record PE/BA/MG IPI activation on approved state transfer files.

Revision ID: 0059_state_pe_ba_mg_ipi
Revises: 0058_state_ce_al_rn_ipi
Create Date: 2026-09-21
"""

from alembic import op

revision = "0059_state_pe_ba_mg_ipi"
down_revision = "0058_state_ce_al_rn_ipi"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.56' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.55' WHERE key = 'implementation_version'")
