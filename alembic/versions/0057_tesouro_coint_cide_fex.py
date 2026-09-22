"""Record Tesouro COINT CIDE/FEX municipal CSV activation.

Revision ID: 0057_tesouro_coint_cide_fex
Revises: 0056_tesouro_iof_ouro_allowlist
Create Date: 2026-09-21
"""

from alembic import op

revision = "0057_tesouro_coint_cide_fex"
down_revision = "0056_tesouro_iof_ouro_allowlist"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.54' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.53' WHERE key = 'implementation_version'")
