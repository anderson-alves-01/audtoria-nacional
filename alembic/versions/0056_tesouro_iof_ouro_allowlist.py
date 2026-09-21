"""Record Tesouro monthly IOF-Ouro allowlist activation.

Revision ID: 0056_tesouro_iof_ouro_allowlist
Revises: 0055_tesouro_lc176_allowlist
Create Date: 2026-09-21
"""

from alembic import op

revision = "0056_tesouro_iof_ouro_allowlist"
down_revision = "0055_tesouro_lc176_allowlist"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.53' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.52' WHERE key = 'implementation_version'")
