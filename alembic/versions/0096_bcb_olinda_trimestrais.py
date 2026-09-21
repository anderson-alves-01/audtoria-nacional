"""Record BCB OLINDA Expectativas trimestrais IPCA/Câmbio/PIB Total.

Revision ID: 0096_bcb_olinda_trimestrais
Revises: 0095_bcb_olinda_mensais_ipa
Create Date: 2026-09-21
"""

from alembic import op

revision = "0096_bcb_olinda_trimestrais"
down_revision = "0095_bcb_olinda_mensais_ipa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.93' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.92' WHERE key = 'implementation_version'")
