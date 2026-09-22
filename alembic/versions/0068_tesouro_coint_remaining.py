"""Record Tesouro COINT FPM/ITR/IOF-Ouro/LC176 municipal activation.

Revision ID: 0068_tesouro_coint_remaining
Revises: 0067_tesouro_lc87_coint
Create Date: 2026-09-21
"""

from alembic import op

revision = "0068_tesouro_coint_remaining"
down_revision = "0067_tesouro_lc87_coint"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.65' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.64' WHERE key = 'implementation_version'")
