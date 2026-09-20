"""Record PR ICMS/IPVA SEFA HTML activation.

Revision ID: 0049_state_pr_activation
Revises: 0048_state_ma_activation
Create Date: 2026-09-20
"""

from alembic import op

revision = "0049_state_pr_activation"
down_revision = "0048_state_ma_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.46' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.45' WHERE key = 'implementation_version'")
