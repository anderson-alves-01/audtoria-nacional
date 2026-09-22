"""Record RN ICMS/IPVA Nextcloud XLS activation.

Revision ID: 0047_state_rn_activation
Revises: 0046_state_pi_ipva_activation
Create Date: 2026-09-20
"""

from alembic import op

revision = "0047_state_rn_activation"
down_revision = "0046_state_pi_ipva_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.44' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.43' WHERE key = 'implementation_version'")
