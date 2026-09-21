"""Record BCB OLINDA Expectativas IPCA Livres e IPCA Servicos.

Revision ID: 0080_bcb_olinda_ipca_livres
Revises: 0079_bcb_olinda_investimento
Create Date: 2026-09-21
"""

from alembic import op

revision = "0080_bcb_olinda_ipca_livres"
down_revision = "0079_bcb_olinda_investimento"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.77' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.76' WHERE key = 'implementation_version'")
