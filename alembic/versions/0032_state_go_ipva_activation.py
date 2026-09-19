"""Record GO IPVA state DataStore activation.

Revision ID: 0032_state_go_ipva_activation
Revises: 0031_state_es_activation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0032_state_go_ipva_activation"
down_revision = "0031_state_es_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.29' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.28' WHERE key = 'implementation_version'")
