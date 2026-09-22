"""Record BCB OLINDA Expectativas mensais IPA-M/IPA-DI/IGP-DI/INPC.

Revision ID: 0095_bcb_olinda_mensais_ipa
Revises: 0094_bcb_olinda_mensais_comp
Create Date: 2026-09-21
"""

from alembic import op

revision = "0095_bcb_olinda_mensais_ipa"
down_revision = "0094_bcb_olinda_mensais_comp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.92' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.91' WHERE key = 'implementation_version'")
