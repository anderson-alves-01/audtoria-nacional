"""Record F4 diagnosis/audit-rules, F8 official-docs, F2 security/backup.

Revision ID: 0020_diagnosis_audit_rules
Revises: 0019_dashboard_observability
Create Date: 2026-09-19
"""

from alembic import op

revision = "0020_diagnosis_audit_rules"
down_revision = "0019_dashboard_observability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.17' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.16' WHERE key = 'implementation_version'")
