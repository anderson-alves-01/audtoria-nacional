"""Record Tesouro monthly FUNDEB complement allowlist.

Revision ID: 0065_tesouro_fundeb_complement
Revises: 0064_state_rs_compensacao_lc194
Create Date: 2026-09-21
"""

from alembic import op

revision = "0065_tesouro_fundeb_complement"
down_revision = "0064_state_rs_compensacao_lc194"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.62' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.61' WHERE key = 'implementation_version'")
