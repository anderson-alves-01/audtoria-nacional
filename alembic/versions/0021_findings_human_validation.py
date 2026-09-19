"""Record F5 findings/cases/human-validation/notifications/collection shells.

Revision ID: 0021_findings_human_validation
Revises: 0020_diagnosis_audit_rules
Create Date: 2026-09-19
"""

from alembic import op

revision = "0021_findings_human_validation"
down_revision = "0020_diagnosis_audit_rules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.18' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.17' WHERE key = 'implementation_version'")
