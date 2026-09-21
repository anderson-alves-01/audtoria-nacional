"""Record BCB OLINDA Expectativas IGP-M/IGP-DI/INPC allowlist expansion.

Revision ID: 0072_bcb_olinda_igp_inpc
Revises: 0071_bcb_olinda_pib
Create Date: 2026-09-21
"""

from alembic import op

revision = "0072_bcb_olinda_igp_inpc"
down_revision = "0071_bcb_olinda_pib"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.69' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.68' WHERE key = 'implementation_version'")
