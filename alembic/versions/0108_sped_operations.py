"""SPED NF-e aggregated operations by UF and CFOP. Additive table only.

Revision ID: 0108_sped_operations
Revises: 0107_user_login_secret
Create Date: 2026-10-27
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0108_sped_operations"
down_revision = "0107_user_login_secret"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sped_operation_facts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("territory_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", sa.String(length=8), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.Column("operacao", sa.String(length=64), nullable=False),
        sa.Column("cfop", sa.String(length=4), nullable=False, server_default=""),
        sa.Column("quantidade", sa.BigInteger(), nullable=False),
        sa.Column("valor_estimado", sa.Numeric(24, 2), nullable=True),
        sa.Column("comparable_quantity", sa.BigInteger(), nullable=True),
        sa.Column("comparable_share", sa.Numeric(9, 6), nullable=True),
        sa.Column("cfop_pairs", sa.Integer(), nullable=True),
        sa.Column("covered_quantity", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["data_load_runs.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["territory_id"], ["territories.id"]),
        sa.CheckConstraint("level in ('SERIE', 'CFOP')", name="ck_sped_facts_level"),
        sa.CheckConstraint("quantidade >= 0", name="ck_sped_facts_quantity"),
        sa.UniqueConstraint(
            "run_id", "level", "ano", "uf", "operacao", "cfop", name="uq_sped_facts_key"
        ),
    )
    op.create_index(
        "ix_sped_facts_scope",
        "sped_operation_facts",
        ["tenant_id", "territory_id", "level", "ano", "uf"],
    )


def downgrade() -> None:
    op.drop_index("ix_sped_facts_scope", table_name="sped_operation_facts")
    op.drop_table("sped_operation_facts")
