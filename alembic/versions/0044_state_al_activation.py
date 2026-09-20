"""Record AL ICMS/IPVA annual XLS activation.

Revision ID: 0044_state_al_activation
Revises: 0043_state_rs_activation
Create Date: 2026-09-20
"""

from alembic import op

revision = "0044_state_al_activation"
down_revision = "0043_state_rs_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.41' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.40' WHERE key = 'implementation_version'")
