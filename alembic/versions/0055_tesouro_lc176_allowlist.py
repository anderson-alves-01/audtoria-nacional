"""Record Tesouro monthly LC176 allowlist activation.

Revision ID: 0055_tesouro_lc176_allowlist
Revises: 0054_tesouro_monthly_allowlist
Create Date: 2026-09-21
"""

from alembic import op

revision = "0055_tesouro_lc176_allowlist"
down_revision = "0054_tesouro_monthly_allowlist"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.52' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.51' WHERE key = 'implementation_version'")
