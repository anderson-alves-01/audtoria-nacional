"""Record BCB OLINDA Expectativas IPC-Fipe, IPA-M and IPA-DI.

Revision ID: 0090_bcb_olinda_ipc_ipa
Revises: 0089_bcb_olinda_ipca15
Create Date: 2026-09-21
"""

from alembic import op

revision = "0090_bcb_olinda_ipc_ipa"
down_revision = "0089_bcb_olinda_ipca15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.87' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.86' WHERE key = 'implementation_version'")
