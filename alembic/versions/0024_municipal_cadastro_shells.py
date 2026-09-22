"""Record F3 municipal uploads and F4 Cadastro 360 empty shells.

Revision ID: 0024_municipal_cadastro_shells
Revises: 0023_f7_f9_f10_shells
Create Date: 2026-09-19
"""

from alembic import op

revision = "0024_municipal_cadastro_shells"
down_revision = "0023_f7_f9_f10_shells"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.21' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.20' WHERE key = 'implementation_version'")
