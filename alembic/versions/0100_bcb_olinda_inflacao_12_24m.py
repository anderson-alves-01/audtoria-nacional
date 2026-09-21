"""Record BCB OLINDA Expectativas Inflacao12/24m activation.

Revision ID: 0100_bcb_olinda_inflacao_12_24m
Revises: 0099_bcb_olinda_selic
Create Date: 2026-09-21
"""

from alembic import op

revision = "0100_bcb_olinda_inflacao_12_24m"
down_revision = "0099_bcb_olinda_selic"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.97' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.96' WHERE key = 'implementation_version'")
