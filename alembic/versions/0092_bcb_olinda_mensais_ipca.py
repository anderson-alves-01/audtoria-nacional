"""Record BCB OLINDA Expectativas mensais IPCA.

Revision ID: 0092_bcb_olinda_mensais_ipca
Revises: 0091_bcb_olinda_balanca_exim
Create Date: 2026-09-21
"""

from alembic import op

revision = "0092_bcb_olinda_mensais_ipca"
down_revision = "0091_bcb_olinda_balanca_exim"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.89' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.88' WHERE key = 'implementation_version'")
