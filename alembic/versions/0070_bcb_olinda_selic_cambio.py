"""Record BCB OLINDA Expectativas Selic+Câmbio allowlist expansion.

Revision ID: 0070_bcb_olinda_selic_cambio
Revises: 0069_bcb_olinda_expectativas
Create Date: 2026-09-21
"""

from alembic import op

revision = "0070_bcb_olinda_selic_cambio"
down_revision = "0069_bcb_olinda_expectativas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.67' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.66' WHERE key = 'implementation_version'")
