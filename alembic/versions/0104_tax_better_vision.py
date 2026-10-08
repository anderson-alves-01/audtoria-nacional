"""Support catalogs and intake lines for the Tax Better vision.

Revision ID: 0104_tax_better_vision
Revises: 0103_gold_finance_state_summary
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0104_tax_better_vision"
down_revision = "0103_gold_finance_state_summary"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tax_better_taxes",
        sa.Column("code", sa.String(length=16), primary_key=True),
    )
    op.create_table(
        "tax_better_organs",
        sa.Column("code", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
    )
    op.create_table(
        "tax_better_fgos",
        sa.Column("code", sa.String(length=32), primary_key=True),
        sa.Column(
            "tax",
            sa.String(length=16),
            sa.ForeignKey("tax_better_taxes.code"),
            nullable=False,
        ),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("pdf_item", sa.String(length=16), nullable=False),
        sa.Column("organ_code", sa.String(length=64), sa.ForeignKey("tax_better_organs.code")),
    )
    op.create_table(
        "tax_better_intake_lines",
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
        sa.Column("organ", sa.String(length=64), nullable=False),
        sa.Column(
            "tax",
            sa.String(length=16),
            sa.ForeignKey("tax_better_taxes.code"),
            nullable=False,
        ),
        sa.Column(
            "fgo_code",
            sa.String(length=32),
            sa.ForeignKey("tax_better_fgos.code"),
            nullable=False,
        ),
        sa.Column("variables", postgresql.JSONB(), nullable=False),
        sa.Column("competence", sa.String(length=16)),
        sa.Column("operation_value", sa.Numeric(24, 4)),
        sa.Column("operation_base", sa.Numeric(24, 4)),
        sa.Column("operation_tax", sa.Numeric(24, 4)),
        sa.Column("malha_value", sa.Numeric(24, 4)),
        sa.Column("malha_base", sa.Numeric(24, 4)),
        sa.Column("malha_tax", sa.Numeric(24, 4)),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_tax_better_intake_scope",
        "tax_better_intake_lines",
        ["tenant_id", "territory_id", "tax", "fgo_code"],
    )
    from sirta_api.domain.tax_better import FGOS, ORGANS, TAXES

    op.bulk_insert(
        sa.table("tax_better_taxes", sa.column("code", sa.String)),
        [{"code": code} for code in TAXES],
    )
    op.bulk_insert(
        sa.table(
            "tax_better_organs",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        list(ORGANS),
    )
    op.bulk_insert(
        sa.table(
            "tax_better_fgos",
            sa.column("code", sa.String),
            sa.column("tax", sa.String),
            sa.column("label", sa.String),
            sa.column("pdf_item", sa.String),
            sa.column("organ_code", sa.String),
        ),
        [
            {
                "code": item["code"],
                "tax": item["tax"],
                "label": item["label"],
                "pdf_item": item["pdfItem"],
                "organ_code": item["organ"],
            }
            for item in FGOS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_tax_better_intake_scope", table_name="tax_better_intake_lines")
    op.drop_table("tax_better_intake_lines")
    op.drop_table("tax_better_fgos")
    op.drop_table("tax_better_organs")
    op.drop_table("tax_better_taxes")
