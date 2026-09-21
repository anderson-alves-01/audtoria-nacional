"""Record BCB OLINDA Expectativas IPCA-15.

Revision ID: 0089_bcb_olinda_ipca15
Revises: 0088_bcb_olinda_prod_ind
Create Date: 2026-09-21
"""

from alembic import op

revision = "0089_bcb_olinda_ipca15"
down_revision = "0088_bcb_olinda_prod_ind"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.86' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.85' WHERE key = 'implementation_version'")
