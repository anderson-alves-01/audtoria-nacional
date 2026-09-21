"""Record BCB OLINDA Expectativas PIB Agropecuária/Indústria allowlist.

Revision ID: 0073_bcb_olinda_pib_sectors
Revises: 0072_bcb_olinda_igp_inpc
Create Date: 2026-09-21
"""

from alembic import op

revision = "0073_bcb_olinda_pib_sectors"
down_revision = "0072_bcb_olinda_igp_inpc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.70' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.69' WHERE key = 'implementation_version'")
