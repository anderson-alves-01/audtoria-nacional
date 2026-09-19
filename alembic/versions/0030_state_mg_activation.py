"""Record MG ICMS/IPVA state CSV.gz activation.

Revision ID: 0030_state_mg_activation
Revises: 0029_state_ba_activation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0030_state_mg_activation"
down_revision = "0029_state_ba_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.27' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.26' WHERE key = 'implementation_version'")
