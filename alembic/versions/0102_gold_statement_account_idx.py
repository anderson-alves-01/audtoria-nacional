"""Index statement account lookups so dashboard revenue sums stay in SQL.

Revision ID: 0102_gold_statement_account_idx
Revises: 0101_doc_homolog_aws_prod
Create Date: 2026-09-28
"""

from alembic import op

revision = "0102_gold_statement_account_idx"
down_revision = "0101_doc_homolog_aws_prod"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_gold_lines_statement_account
        ON gold_official_lines (source_id, (payload ->> 'account'))
        WHERE source_id IN ('SICONFI-RREO', 'SICONFI-DCA')
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_gold_lines_statement_account")
