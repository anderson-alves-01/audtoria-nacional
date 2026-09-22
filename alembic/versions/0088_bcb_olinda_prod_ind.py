"""Record BCB OLINDA Expectativas Produção industrial.

Revision ID: 0088_bcb_olinda_prod_ind
Revises: 0087_bcb_olinda_pib_importacao
Create Date: 2026-09-21
"""

from alembic import op

revision = "0088_bcb_olinda_prod_ind"
down_revision = "0087_bcb_olinda_pib_importacao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.85' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.84' WHERE key = 'implementation_version'")
