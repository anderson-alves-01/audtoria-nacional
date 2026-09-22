"""Record SC SEF Anual_2017 ICMS/IPVA/IPI activation.

Revision ID: 0098_state_sc_activation
Revises: 0097_bcb_olinda_trim_pib_sec
Create Date: 2026-09-21
"""

from alembic import op

revision = "0098_state_sc_activation"
down_revision = "0097_bcb_olinda_trim_pib_sec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.95' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.94' WHERE key = 'implementation_version'")
