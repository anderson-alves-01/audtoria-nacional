"""Store municipal money already summed by state.

Revision ID: 0103_gold_finance_state_summary
Revises: 0102_gold_statement_account_idx
Create Date: 2026-09-28
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0103_gold_finance_state_summary"
down_revision = "0102_gold_statement_account_idx"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gold_finance_state_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "territory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("territories.id"),
            nullable=False,
        ),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("uf_code", sa.String(length=2), nullable=False),
        sa.Column("competence", sa.String(length=4), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("total", sa.Numeric(24, 4), nullable=False),
        sa.Column("municipality_count", sa.Integer(), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "territory_id",
            "source_id",
            "uf_code",
            "competence",
            name="uq_gold_finance_state_summary",
        ),
    )
    op.create_index(
        "ix_gold_finance_state_summary_scope",
        "gold_finance_state_summaries",
        ["tenant_id", "territory_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_gold_finance_state_summary_scope", table_name="gold_finance_state_summaries")
    op.drop_table("gold_finance_state_summaries")
