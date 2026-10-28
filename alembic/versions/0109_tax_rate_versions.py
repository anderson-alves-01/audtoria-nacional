"""Versioned tax rates by validity, with legal basis and validation status. Additive table only.

Revision ID: 0109_tax_rate_versions
Revises: 0108_sped_operations
Create Date: 2026-10-27

Only the Acre ICMS modal rate is VALIDADO (user confirmation of 2026-10-27, LC/AC 422/2022).
Every other rate is PENDENTE: it has no legal basis, no start date and no official URL yet, and the
application never presents it as legally validated. Unknown values stay NULL, never invented.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0109_tax_rate_versions"
down_revision = "0108_sped_operations"
branch_labels = None
depends_on = None

AC_BASIS = (
    "Lei Complementar Estadual nº 422, de 26/12/2022, que alterou o art. 18 da Lei Complementar "
    "nº 55/1997 (Acre). Alíquota modal interna; há exceções por mercadoria e operação."
)
AC_BASIS_BEFORE = (
    "Redação anterior do art. 18 da Lei Complementar nº 55/1997 (Acre), vigente até a "
    "LC/AC 422/2022. "
    "Dispositivo e data de início a anexar. Alíquota modal interna."
)
AC_VALIDATED_BY = "responsável do projeto, informado em 2026-10-27"
IMAGE_NOTE = (
    "Lida do anexo de ICMS por UF enviado pelo usuário em 2026-10-27; sem lei, vigência ou URL."
)
REQUIREMENT_NOTE = "Alíquota informada no requisito do Simulador; sem lei, vigência ou URL."

ICMS_PENDING = {
    "AL": "20.5", "AP": "18", "AM": "20", "BA": "20.5", "CE": "20", "DF": "20", "ES": "17",
    "GO": "19", "MA": "23", "MT": "17", "MS": "17", "MG": "18", "PA": "19", "PB": "20",
    "PR": "19.5", "PE": "20.5", "PI": "22.5", "RJ": "20", "RN": "20", "RS": "17", "RO": "19.5",
    "RR": "20", "SC": "17", "SP": "18", "SE": "19", "TO": "20",
}  # fmt: skip
FLAT_PENDING = {"ITCD": "6", "ITBI": "3", "ISS": "5"}


def _rows() -> list[dict]:
    rows: list[dict] = [
        {
            "tax": "ICMS",
            "uf": "AC",
            "rate_kind": "MODAL",
            "rate": "17",
            "valid_from": None,
            "valid_to": date(2023, 3, 31),
            "legal_basis": AC_BASIS_BEFORE,
            "official_url": None,
            "status": "VALIDADO",
            "validated_by": AC_VALIDATED_BY,
            "note": "Início legal anterior a 2021 não conferido; vale de 2021 a mar/2023.",
        },
        {
            "tax": "ICMS",
            "uf": "AC",
            "rate_kind": "MODAL",
            "rate": "19",
            "valid_from": date(2023, 4, 1),
            "valid_to": None,
            "legal_basis": AC_BASIS,
            "official_url": None,
            "status": "VALIDADO",
            "validated_by": AC_VALIDATED_BY,
            "note": "URL oficial (legis.ac.gov.br) a anexar.",
        },
    ]
    for uf, rate in ICMS_PENDING.items():
        rows.append(
            {
                "tax": "ICMS",
                "uf": uf,
                "rate_kind": "MODAL",
                "rate": rate,
                "valid_from": None,
                "valid_to": None,
                "legal_basis": None,
                "official_url": None,
                "status": "PENDENTE",
                "validated_by": None,
                "note": IMAGE_NOTE,
            }
        )
    for tax, rate in FLAT_PENDING.items():
        rows.append(
            {
                "tax": tax,
                "uf": "BR",
                "rate_kind": "UNICA",
                "rate": rate,
                "valid_from": None,
                "valid_to": None,
                "legal_basis": None,
                "official_url": None,
                "status": "PENDENTE",
                "validated_by": None,
                "note": REQUIREMENT_NOTE,
            }
        )
    return rows  # fmt: skip


def upgrade() -> None:
    table = op.create_table(
        "tax_rate_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tax", sa.String(length=8), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.Column("rate_kind", sa.String(length=16), nullable=False),
        sa.Column("rate", sa.Numeric(7, 4), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("legal_basis", sa.Text(), nullable=True),
        sa.Column("official_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("validated_by", sa.String(length=160), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("tax in ('ICMS', 'ITCD', 'ITBI', 'ISS')", name="ck_tax_rate_tax"),
        sa.CheckConstraint(
            "rate_kind in ('MODAL', 'ESPECIFICA', 'INTERESTADUAL', 'UNICA')",
            name="ck_tax_rate_kind",
        ),
        sa.CheckConstraint("rate >= 0 and rate <= 100", name="ck_tax_rate_range"),
        sa.CheckConstraint(
            "status in ('PENDENTE', 'VALIDADO', 'REVOGADO')", name="ck_tax_rate_status"
        ),
        sa.CheckConstraint(
            "valid_to is null or valid_from is null or valid_to >= valid_from",
            name="ck_tax_rate_window",
        ),
        # A validated rate must carry who validated it and its legal basis.
        sa.CheckConstraint(
            "status <> 'VALIDADO' or (legal_basis is not null and validated_by is not null)",
            name="ck_tax_rate_validated_basis",
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_tax_rate_version ON tax_rate_versions "
        "(tax, uf, rate_kind, coalesce(valid_from, date '0001-01-01'))"
    )
    op.create_index("ix_tax_rate_lookup", "tax_rate_versions", ["tax", "uf", "status"])
    op.bulk_insert(
        table,
        [
            {
                **row,
                "rate": Decimal(row["rate"]),
                "id": uuid4(),
                "validated_at": None,
                "created_at": datetime(2026, 10, 27, 22, 0, tzinfo=UTC),
            }
            for row in _rows()
        ],
    )
    # Validation date of the two Acre rows is the confirmation date.
    op.execute(
        "UPDATE tax_rate_versions SET validated_at = timestamptz '2026-10-27 22:00:00-03' "
        "WHERE status = 'VALIDADO'"
    )


def downgrade() -> None:
    op.drop_index("ix_tax_rate_lookup", table_name="tax_rate_versions")
    op.execute("DROP INDEX IF EXISTS uq_tax_rate_version")
    op.drop_table("tax_rate_versions")
