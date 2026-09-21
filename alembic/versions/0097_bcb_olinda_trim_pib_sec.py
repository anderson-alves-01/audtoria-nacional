"""Record BCB OLINDA Expectativas trimestrais PIB setoriais.

Revision ID: 0097_bcb_olinda_trim_pib_sec
Revises: 0096_bcb_olinda_trimestrais
Create Date: 2026-09-21
"""

from alembic import op

revision = "0097_bcb_olinda_trim_pib_sec"
down_revision = "0096_bcb_olinda_trimestrais"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.94' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.93' WHERE key = 'implementation_version'")
