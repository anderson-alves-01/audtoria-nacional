"""Record BCB OLINDA Expectativas Balança Exportações/Importações.

Revision ID: 0091_bcb_olinda_balanca_exim
Revises: 0090_bcb_olinda_ipc_ipa
Create Date: 2026-09-21
"""

from alembic import op

revision = "0091_bcb_olinda_balanca_exim"
down_revision = "0090_bcb_olinda_ipc_ipa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.88' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.87' WHERE key = 'implementation_version'")
