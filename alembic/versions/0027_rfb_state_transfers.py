"""Record RFB territorial connector and state ICMS/IPVA provenance shell.

Revision ID: 0027_rfb_state_transfers
Revises: 0026_controlled_backfill
Create Date: 2026-09-19
"""

from alembic import op

revision = "0027_rfb_state_transfers"
down_revision = "0026_controlled_backfill"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.24' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.23' WHERE key = 'implementation_version'")
