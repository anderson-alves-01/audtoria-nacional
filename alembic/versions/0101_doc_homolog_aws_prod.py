"""Record DOC-HOMOLOGATION package + AWS prod stack code (G10 gated).

Revision ID: 0101_doc_homolog_aws_prod
Revises: 0100_bcb_olinda_inflacao_12_24m
Create Date: 2026-09-21
"""

from alembic import op

revision = "0101_doc_homolog_aws_prod"
down_revision = "0100_bcb_olinda_inflacao_12_24m"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.98' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.97' WHERE key = 'implementation_version'")
