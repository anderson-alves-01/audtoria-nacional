"""Record BCB OLINDA Expectativas PIB Total+Serviços allowlist expansion.

Revision ID: 0071_bcb_olinda_pib
Revises: 0070_bcb_olinda_selic_cambio
Create Date: 2026-09-21
"""

from alembic import op

revision = "0071_bcb_olinda_pib"
down_revision = "0070_bcb_olinda_selic_cambio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.68' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.67' WHERE key = 'implementation_version'")
