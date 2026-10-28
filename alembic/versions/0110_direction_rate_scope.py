"""Transfer direction on SPED facts; jurisdiction scope and homologation on tax rates. Additive.

Revision ID: 0110_direction_rate_scope
Revises: 0109_tax_rate_versions
Create Date: 2026-10-28

What this adds, and only this:
- sped_operation_facts.direcao (RECEBIDA or REMETIDA). Existing rows are all outbound, so the
  rows of the operation "Transferências" are marked REMETIDA. No fact is rewritten or removed.
- tax_rate_versions: jurisdiction_level (UF, MUNICIPIO, SIMULACAO), municipality_ibge_code,
  operation_ref, reference_min/reference_max, homologated_by/homologated_at.
- The unique index is replaced by one that also looks at locality and operation (DDL on a table
  that has not reached production: 0109 is not deployed). No rate row is deleted.
- Acre ICMS rows receive their legal documentation (official pages and start of validity).
  They stay not homologated: homologation is a separate human step.
- ITCD, ITBI and ISS flat values become SIMULACAO parameters, which can never be VALIDADO.
"""

import sqlalchemy as sa
from alembic import op

revision = "0110_direction_rate_scope"
down_revision = "0109_tax_rate_versions"
branch_labels = None
depends_on = None

LC422_URL = "https://sefaz.ac.gov.br/2021/?p=11479"
LC55_URL = "https://sefaz.ac.gov.br/2021/?p=12159"
AC_19_BASIS = (
    "Lei Complementar Estadual nº 55/1997, art. 18, I, com a redação da Lei Complementar "
    "Estadual nº 422, de 26/12/2022, com efeitos a partir de 01/04/2023. Alíquota modal interna "
    f"de 19%, ressalvadas as hipóteses de alíquota específica. Texto consolidado: {LC55_URL}"
)
AC_19_NOTE = (
    "Documentação jurídica completa (páginas da Sefaz/AC). Não homologada: falta o revisor "
    "responsável e a conferência das condições de aplicação (exceções por mercadoria)."
)
AC_17_BASIS = (
    "Lei Complementar Estadual nº 55/1997, art. 18, I, com a redação da Lei Complementar "
    "Estadual nº 100, de 18/12/2001, com efeitos de 01/01/2002 até 31/03/2023. Alíquota modal "
    "interna de 17%. Redação conferida no texto consolidado da LC 55/1997."
)
AC_17_NOTE = (
    "Vigência inicial 01/01/2002 conforme o texto consolidado da LC 55/1997. Não homologada: "
    "falta o revisor responsável e a conferência das condições de aplicação."
)
SIMULATION_NOTE = (
    "Parâmetro de simulação do requisito do Simulador. Não é alíquota de UF nem de município "
    "e não pode ser homologado como alíquota única nacional."
)
ITCD_LIMIT_NOTE = (
    " Limite de referência de 8%: Resolução do Senado nº 9/1992 (informado pelo responsável, "
    "a conferir na fonte)."
)
ISS_LIMIT_NOTE = (
    " Limites de referência de 2% a 5%: LC nº 116/2003 (informado pelo responsável, a conferir "
    "na fonte)."
)


def upgrade() -> None:
    # --- SPED: direction of transfers ------------------------------------------------------
    op.add_column("sped_operation_facts", sa.Column("direcao", sa.String(length=8), nullable=True))
    op.create_check_constraint(
        "ck_sped_facts_direcao",
        "sped_operation_facts",
        "direcao is null or direcao in ('RECEBIDA', 'REMETIDA')",
    )
    op.execute(
        "UPDATE sped_operation_facts SET direcao = 'REMETIDA' "
        "WHERE operacao = 'Transferências' AND direcao IS NULL"
    )

    # --- Rates: scope, reference limits and human homologation ----------------------------
    op.add_column(
        "tax_rate_versions",
        sa.Column("jurisdiction_level", sa.String(length=12), nullable=False, server_default="UF"),
    )
    op.add_column(
        "tax_rate_versions", sa.Column("municipality_ibge_code", sa.String(length=7), nullable=True)
    )
    op.add_column(
        "tax_rate_versions", sa.Column("operation_ref", sa.String(length=64), nullable=True)
    )
    op.add_column("tax_rate_versions", sa.Column("reference_min", sa.Numeric(7, 4), nullable=True))
    op.add_column("tax_rate_versions", sa.Column("reference_max", sa.Numeric(7, 4), nullable=True))
    op.add_column(
        "tax_rate_versions", sa.Column("homologated_by", sa.String(length=160), nullable=True)
    )
    op.add_column(
        "tax_rate_versions", sa.Column("homologated_at", sa.DateTime(timezone=True), nullable=True)
    )

    op.execute("UPDATE tax_rate_versions SET jurisdiction_level = 'SIMULACAO' WHERE uf = 'BR'")
    op.execute(
        "UPDATE tax_rate_versions SET note = '" + SIMULATION_NOTE + "' "
        "WHERE jurisdiction_level = 'SIMULACAO'"
    )
    op.execute(
        "UPDATE tax_rate_versions SET reference_max = 8, note = note || '"
        + ITCD_LIMIT_NOTE
        + "' WHERE jurisdiction_level = 'SIMULACAO' AND tax = 'ITCD'"
    )
    op.execute(
        "UPDATE tax_rate_versions SET reference_min = 2, reference_max = 5, note = note || '"
        + ISS_LIMIT_NOTE
        + "' WHERE jurisdiction_level = 'SIMULACAO' AND tax = 'ISS'"
    )

    op.create_check_constraint(
        "ck_tax_rate_jurisdiction",
        "tax_rate_versions",
        "jurisdiction_level in ('UF', 'MUNICIPIO', 'SIMULACAO')",
    )
    op.create_check_constraint(
        "ck_tax_rate_simulation_not_validated",
        "tax_rate_versions",
        "jurisdiction_level <> 'SIMULACAO' or status = 'PENDENTE'",
    )
    op.create_check_constraint(
        "ck_tax_rate_municipality_code",
        "tax_rate_versions",
        "jurisdiction_level <> 'MUNICIPIO' or municipality_ibge_code is not null",
    )
    op.create_check_constraint(
        "ck_tax_rate_reference_window",
        "tax_rate_versions",
        "reference_min is null or reference_max is null or reference_min <= reference_max",
    )
    op.create_check_constraint(
        "ck_tax_rate_homologated_validated",
        "tax_rate_versions",
        "homologated_by is null or status = 'VALIDADO'",
    )

    op.execute("DROP INDEX IF EXISTS uq_tax_rate_version")
    op.execute(
        "CREATE UNIQUE INDEX uq_tax_rate_version_v2 ON tax_rate_versions "
        "(tax, uf, rate_kind, jurisdiction_level, coalesce(municipality_ibge_code, ''), "
        "coalesce(operation_ref, ''), coalesce(valid_from, date '0001-01-01'))"
    )

    # --- Acre ICMS: legal documentation only; homologation stays with the reviewer --------
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE tax_rate_versions SET legal_basis = :basis, official_url = :url, "
            "valid_from = :valid_from, note = :note "
            "WHERE tax = 'ICMS' AND uf = 'AC' AND rate = 19 AND valid_from = date '2023-04-01'"
        ),
        {
            "basis": AC_19_BASIS,
            "url": LC422_URL,
            "valid_from": "2023-04-01",
            "note": AC_19_NOTE,
        },
    )
    bind.execute(
        sa.text(
            "UPDATE tax_rate_versions SET legal_basis = :basis, official_url = :url, "
            "valid_from = date '2002-01-01', note = :note "
            "WHERE tax = 'ICMS' AND uf = 'AC' AND rate = 17 AND valid_from IS NULL "
            "AND valid_to = date '2023-03-31'"
        ),
        {"basis": AC_17_BASIS, "url": LC55_URL, "note": AC_17_NOTE},
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_tax_rate_version_v2")
    op.execute(
        "CREATE UNIQUE INDEX uq_tax_rate_version ON tax_rate_versions "
        "(tax, uf, rate_kind, coalesce(valid_from, date '0001-01-01'))"
    )
    for name in (
        "ck_tax_rate_homologated_validated",
        "ck_tax_rate_reference_window",
        "ck_tax_rate_municipality_code",
        "ck_tax_rate_simulation_not_validated",
        "ck_tax_rate_jurisdiction",
    ):
        op.drop_constraint(name, "tax_rate_versions", type_="check")
    for column in (
        "homologated_at",
        "homologated_by",
        "reference_max",
        "reference_min",
        "operation_ref",
        "municipality_ibge_code",
        "jurisdiction_level",
    ):
        op.drop_column("tax_rate_versions", column)
    op.drop_constraint("ck_sped_facts_direcao", "sped_operation_facts", type_="check")
    op.drop_column("sped_operation_facts", "direcao")
