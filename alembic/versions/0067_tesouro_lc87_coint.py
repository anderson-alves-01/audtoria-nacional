"""Record Tesouro COINT LC 87/96 municipal activation.

Revision ID: 0067_tesouro_lc87_coint
Revises: 0066_tesouro_fundeb_coint
Create Date: 2026-09-21
"""

from alembic import op

revision = "0067_tesouro_lc87_coint"
down_revision = "0066_tesouro_fundeb_coint"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.64' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.63' WHERE key = 'implementation_version'")
