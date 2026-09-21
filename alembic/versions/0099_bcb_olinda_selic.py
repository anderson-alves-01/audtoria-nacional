"""Record BCB OLINDA ExpectativasMercadoSelic activation.

Revision ID: 0099_bcb_olinda_selic
Revises: 0098_state_sc_activation
Create Date: 2026-09-21
"""

from alembic import op

revision = "0099_bcb_olinda_selic"
down_revision = "0098_state_sc_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.96' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.95' WHERE key = 'implementation_version'")
