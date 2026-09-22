"""Record AC Transparência monthly ICMS and FUNDEB on approved JSON.

Revision ID: 0063_ac_tr_icms_fundeb
Revises: 0062_state_es_frd_compensacao
Create Date: 2026-09-21
"""

from alembic import op

revision = "0063_ac_tr_icms_fundeb"
down_revision = "0062_state_es_frd_compensacao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.60' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.59' WHERE key = 'implementation_version'")
