"""Record BCB OLINDA Expectativas PIB Formação Bruta de Capital Fixo.

Revision ID: 0083_bcb_olinda_pib_fbcf
Revises: 0082_bcb_olinda_ipca_bens
Create Date: 2026-09-21
"""

from alembic import op

revision = "0083_bcb_olinda_pib_fbcf"
down_revision = "0082_bcb_olinda_ipca_bens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.80' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.79' WHERE key = 'implementation_version'")
