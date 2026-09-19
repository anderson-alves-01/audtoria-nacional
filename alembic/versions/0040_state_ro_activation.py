"""Record RO ICMS/IPVA state CSV activation.

Revision ID: 0040_state_ro_activation
Revises: 0039_cnes_demas_uf_activation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0040_state_ro_activation"
down_revision = "0039_cnes_demas_uf_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.37' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.36' WHERE key = 'implementation_version'")
