"""Record BCB OLINDA Expectativas Taxa de desocupação.

Revision ID: 0078_bcb_olinda_taxa_desocup
Revises: 0077_bcb_olinda_divida_bruta
Create Date: 2026-09-21
"""

from alembic import op

revision = "0078_bcb_olinda_taxa_desocup"
down_revision = "0077_bcb_olinda_divida_bruta"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.75' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.74' WHERE key = 'implementation_version'")
