"""Record BCB OLINDA Expectativas mensais IGP-M + Câmbio.

Revision ID: 0093_bcb_olinda_igp_cambio
Revises: 0092_bcb_olinda_mensais_ipca
Create Date: 2026-09-21
"""

from alembic import op

revision = "0093_bcb_olinda_igp_cambio"
down_revision = "0092_bcb_olinda_mensais_ipca"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.90' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.89' WHERE key = 'implementation_version'")
