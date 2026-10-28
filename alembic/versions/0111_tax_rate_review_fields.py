"""Rate restrictions and human review fields; Acre ICMS primary source. Additive.

Revision ID: 0111_tax_rate_review_fields
Revises: 0110_direction_rate_scope
Create Date: 2026-10-28

What this adds, and only this:
- tax_rate_versions.restrictions, reviewed_by, reviewed_at (all nullable). A review is a human
  step: reviewed_by and reviewed_at are both filled or both empty.
- Acre ICMS 19% (from 01/04/2023): the official URL becomes the primary text of Lei Complementar
  Estadual nº 422/2022 (https://www.legis.ac.gov.br/detalhar/5461), the Sefaz pages stay as
  complementary sources, and the exceptions listed in the article are registered.
- Nothing is homologated or reviewed here: reviewed_by, reviewed_at and homologated_by stay NULL.
  The other 26 UFs and ITCD/ITBI/ISS are not touched.
"""

import sqlalchemy as sa
from alembic import op

revision = "0111_tax_rate_review_fields"
down_revision = "0110_direction_rate_scope"
branch_labels = None
depends_on = None

LC422_PRIMARY_URL = "https://www.legis.ac.gov.br/detalhar/5461"
SEFAZ_LC422_URL = "https://sefaz.ac.gov.br/2021/?p=11479"
SEFAZ_LC55_URL = "https://sefaz.ac.gov.br/2021/?p=12159"
AC_19_BASIS = (
    "Lei Complementar Estadual nº 55/1997, art. 18, I, com a redação da Lei Complementar "
    "Estadual nº 422, de 26/12/2022 (publicada em 27/12/2022), com efeitos a partir de "
    "01/04/2023. Alíquota modal interna de 19%, ressalvadas as hipóteses de alíquota "
    f"específica. Fonte primária: {LC422_PRIMARY_URL}. Páginas complementares da Sefaz/AC: "
    f"{SEFAZ_LC422_URL} e {SEFAZ_LC55_URL}."
)
AC_19_RESTRICTIONS = (
    "A alíquota de 19% vale para operações e prestações internas, ressalvadas as hipóteses de "
    "alíquota específica do art. 18 da LC 55/1997. Exceções constantes do texto da LC 422/2022: "
    "12% nas operações e prestações interestaduais (art. 18, II, a) e em serviços de comunicação "
    "para empreendimentos de telemarketing e call center (II, b); 25% internas para joias, "
    "semijoias, bijuterias, perfumes e cosméticos (com exceções), e para cervejas sem álcool, "
    "refrigerantes e águas minerais (com exceção); 27% cervejas e chopes; 30% fumos e derivados; "
    "33% bebidas alcoólicas exceto cervejas e chopes; 17% produtos da cesta básica definidos no "
    "regulamento do ICMS. O texto publicado na página omite itens do inciso III (reticências): "
    "a lista completa de exceções não foi transcrita e precisa ser conferida pelo revisor."
)
AC_19_NOTE = (
    "Documentação jurídica completa e exceções registradas. Não homologada: falta a revisão "
    "humana (responsável e data), a conferência da lista completa de exceções e a homologação "
    "pelo responsável."
)


def upgrade() -> None:
    op.add_column("tax_rate_versions", sa.Column("restrictions", sa.Text(), nullable=True))
    op.add_column(
        "tax_rate_versions", sa.Column("reviewed_by", sa.String(length=160), nullable=True)
    )
    op.add_column(
        "tax_rate_versions", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_check_constraint(
        "ck_tax_rate_review_pair",
        "tax_rate_versions",
        "(reviewed_by is null) = (reviewed_at is null)",
    )
    op.create_check_constraint(
        "ck_tax_rate_homologated_reviewed",
        "tax_rate_versions",
        "homologated_by is null or reviewed_by is not null",
    )
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE tax_rate_versions SET legal_basis = :basis, official_url = :url, "
            "restrictions = :restrictions, note = :note "
            "WHERE tax = 'ICMS' AND uf = 'AC' AND rate = 19 AND valid_from = date '2023-04-01' "
            "AND homologated_by IS NULL"
        ),
        {
            "basis": AC_19_BASIS,
            "url": LC422_PRIMARY_URL,
            "restrictions": AC_19_RESTRICTIONS,
            "note": AC_19_NOTE,
        },
    )


def downgrade() -> None:
    # Restore the Sefaz page as the official URL of the 19% row (state left by 0110).
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE tax_rate_versions SET official_url = :url "
            "WHERE tax = 'ICMS' AND uf = 'AC' AND rate = 19 AND valid_from = date '2023-04-01' "
            "AND official_url = :primary"
        ),
        {"url": SEFAZ_LC422_URL, "primary": LC422_PRIMARY_URL},
    )
    op.drop_constraint("ck_tax_rate_homologated_reviewed", "tax_rate_versions", type_="check")
    op.drop_constraint("ck_tax_rate_review_pair", "tax_rate_versions", type_="check")
    op.drop_column("tax_rate_versions", "reviewed_at")
    op.drop_column("tax_rate_versions", "reviewed_by")
    op.drop_column("tax_rate_versions", "restrictions")
