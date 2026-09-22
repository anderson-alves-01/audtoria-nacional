"""Record BCB OLINDA Expectativas Focus (IPCA) activation.

Revision ID: 0069_bcb_olinda_expectativas
Revises: 0068_tesouro_coint_remaining
Create Date: 2026-09-21
"""

from alembic import op

revision = "0069_bcb_olinda_expectativas"
down_revision = "0068_tesouro_coint_remaining"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.66' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.65' WHERE key = 'implementation_version'")
