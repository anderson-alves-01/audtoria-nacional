"""Record F6 payments, active-debt and Procuradoria empty shells.

Revision ID: 0022_f6_payments_active_debt
Revises: 0021_findings_human_validation
Create Date: 2026-09-19
"""

from alembic import op

revision = "0022_f6_payments_active_debt"
down_revision = "0021_findings_human_validation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.19' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.18' WHERE key = 'implementation_version'")
