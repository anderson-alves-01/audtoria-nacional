"""Record PE ICMS/IPVA state CSV activation.

Revision ID: 0028_state_pe_activation
Revises: 0027_rfb_state_transfers
Create Date: 2026-09-19
"""

from alembic import op

revision = "0028_state_pe_activation"
down_revision = "0027_rfb_state_transfers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.25' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.24' WHERE key = 'implementation_version'")
