"""Record BCB OLINDA Expectativas IPCA Bens industrializados.

Revision ID: 0082_bcb_olinda_ipca_bens
Revises: 0081_bcb_olinda_ipca_admin
Create Date: 2026-09-21
"""

from alembic import op

revision = "0082_bcb_olinda_ipca_bens"
down_revision = "0081_bcb_olinda_ipca_admin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.79' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.78' WHERE key = 'implementation_version'")
