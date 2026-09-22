"""Record BCB OLINDA Expectativas Dívida + Balança Saldo allowlist.

Revision ID: 0074_bcb_olinda_divida_balanca
Revises: 0073_bcb_olinda_pib_sectors
Create Date: 2026-09-21
"""

from alembic import op

revision = "0074_bcb_olinda_divida_balanca"
down_revision = "0073_bcb_olinda_pib_sectors"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.71' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.70' WHERE key = 'implementation_version'")
