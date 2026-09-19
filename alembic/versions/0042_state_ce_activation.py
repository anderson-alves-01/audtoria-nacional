"""Record CE ICMS/IPVA state XLS activation.

Revision ID: 0042_state_ce_activation
Revises: 0041_state_ac_activation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0042_state_ce_activation"
down_revision = "0041_state_ac_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.39' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.38' WHERE key = 'implementation_version'")
