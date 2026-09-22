"""Record ANP revendedores UF-scoped activation.

Revision ID: 0034_anp_revendedores_activation
Revises: 0033_state_ms_activation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0034_anp_revendedores_activation"
down_revision = "0033_state_ms_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.31' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.30' WHERE key = 'implementation_version'")
