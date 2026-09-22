"""Record PA ICMS Verde SEMAS XLSX activation (ecological component).

Revision ID: 0050_state_pa_icms_verde
Revises: 0049_state_pr_activation
Create Date: 2026-09-20
"""

from alembic import op

revision = "0050_state_pa_icms_verde"
down_revision = "0049_state_pr_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.47' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.46' WHERE key = 'implementation_version'")
