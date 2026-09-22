"""Record ES FRD and CompensacaoFinanceira on approved transfer CSV.

Revision ID: 0062_state_es_frd_compensacao
Revises: 0061_state_al_pr_royalty
Create Date: 2026-09-21
"""

from alembic import op

revision = "0062_state_es_frd_compensacao"
down_revision = "0061_state_al_pr_royalty"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.59' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.58' WHERE key = 'implementation_version'")
