# ruff: noqa: E501  (long Portuguese report sentences)
"""Report what is missing before each seeded tax rate counts as homologated.

Read only and offline. It reads the seed rows of alembic/versions/0109_tax_rate_versions.py, overlays
what alembic/versions/0110_direction_rate_scope.py changes (Acre documentation, simulation scope) and
applies sirta_api.domain.tax_rates.homologation_gaps to each one. It does not connect to any
database and never changes a rate or a status. It writes evidence/ops/aliquotas-homologacao-<date>.md.

Usage: python tools/ops/tax-rates-audit.py
"""

from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sirta_api.domain.tax_rates import homologation_gaps  # noqa: E402

MIGRATION = ROOT / "alembic" / "versions" / "0109_tax_rate_versions.py"
MIGRATION_SCOPE = ROOT / "alembic" / "versions" / "0110_direction_rate_scope.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_seed_rows(path: Path = MIGRATION, scope: Path = MIGRATION_SCOPE) -> list[dict]:
    """Rows as they stand after migrations 0109 and 0110."""
    rows = [dict(row) for row in _load_module("tax_rate_versions_seed", path)._rows()]
    patch = _load_module("tax_rate_scope_patch", scope)
    for row in rows:
        row["jurisdiction_level"] = "SIMULACAO" if row["uf"] == "BR" else "UF"
        row["homologated_by"] = None
        if row["tax"] == "ICMS" and row["uf"] == "AC":
            if row["rate"] == "19":
                row["legal_basis"], row["official_url"] = patch.AC_19_BASIS, patch.LC422_URL
            else:
                row["legal_basis"], row["official_url"] = patch.AC_17_BASIS, patch.LC55_URL
                row["valid_from"] = date(2002, 1, 1)
    return rows


def gaps_of(row: dict) -> list[str]:
    return homologation_gaps(
        status=row["status"],
        legal_basis=row["legal_basis"],
        official_url=row["official_url"],
        validated_by=row["validated_by"],
        valid_from=row["valid_from"],
        homologated_by=row["homologated_by"],
        jurisdiction_level=row["jurisdiction_level"],
    )


def _date(value) -> str:
    return value.isoformat() if value else "—"


def build_report(rows: list[dict], stamp: str) -> str:
    audited = [(row, gaps_of(row)) for row in rows]
    homologated = [row for row, gaps in audited if not gaps]
    by_status = Counter(row["status"] for row in rows)
    by_gap = Counter(gap for _row, gaps in audited for gap in gaps)
    lines = [
        f"# Alíquotas: lacunas para a homologação ({stamp})",
        "",
        "Gerado por `tools/ops/tax-rates-audit.py`, somente leitura, a partir das linhas semeadas pela "
        "migração `0109_tax_rate_versions` e pelo ajuste da `0110_direction_rate_scope`. Nenhuma alíquota ou status foi alterado.",
        "",
        "Critério de homologação: status `VALIDADO` e, ao mesmo tempo, fundamento legal, URL oficial da "
        "legislação, responsável pela validação, início da vigência conhecido e **homologação pelo "
        "responsável** (etapa humana separada: preencher a documentação não homologa). Percentual lido "
        "de uma imagem não atende a nenhum desses itens. Parâmetro de simulação (`SIMULACAO`) nunca é "
        "homologado como alíquota de UF ou município.",
        "",
        "## Resumo",
        "",
        f"- Versões de alíquota: {len(rows)}.",
        f"- Homologadas: **{len(homologated)}**.",
        "- Por status: "
        + ", ".join(f"{status} {count}" for status, count in sorted(by_status.items()))
        + ".",
        "",
        "| Lacuna | Versões afetadas |",
        "| --- | ---: |",
    ]
    for gap, count in sorted(by_gap.items(), key=lambda item: -item[1]):
        lines.append(f"| {gap} | {count} |")
    lines += ["", "## ICMS por UF", ""]
    lines += [
        "| UF | Alíquota (%) | Início | Fim | Status | Lacunas |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    icms = sorted(
        (item for item in audited if item[0]["tax"] == "ICMS"),
        key=lambda i: (i[0]["uf"], str(i[0]["valid_from"])),
    )
    for row, gaps in icms:
        lines.append(
            f"| {row['uf']} | {row['rate']} | {_date(row['valid_from'])} | {_date(row['valid_to'])} | "
            f"{row['status']} | {'; '.join(gaps) or 'nenhuma'} |"
        )
    lines += ["", "## ITCD, ITBI e ISS", ""]
    lines += [
        "| Imposto | Competência | Nível | Alíquota (%) | Status | Lacunas |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    competence = {"ITCD": "estadual", "ITBI": "municipal", "ISS": "municipal"}
    for row, gaps in audited:
        if row["tax"] != "ICMS":
            lines.append(
                f"| {row['tax']} | {competence[row['tax']]} | {row['jurisdiction_level']} | {row['rate']} | "
                f"{row['status']} | {'; '.join(gaps) or 'nenhuma'} |"
            )
    lines += [
        "",
        "Os valores de 6%, 3% e 5% são parâmetros de simulação do requisito do Simulador. Não existe alíquota única nacional de ITCD, ITBI ou ISS: o cadastro relaciona imposto, localidade (UF ou município), operação, fundamento legal e vigência.",
        "",
        "## O que falta informar",
        "",
        "- AC: a documentação jurídica está completa (LC/AC 55/1997 art. 18, I, redação da LC/AC 422/2022, vigência 01/04/2023; redação anterior da LC/AC 100/2001, vigência 01/01/2002 a 31/03/2023, páginas da Sefaz/AC). Falta o responsável conferir os endereços e as condições de aplicação (exceções por mercadoria) e registrar a homologação.",
        "- 26 UFs: lei ou decreto da alíquota modal, início da vigência, URL oficial, responsável pela validação e homologação, uma UF por vez.",
        "- ITCD (estadual): lei de cada UF, alíquota, faixas, base e vigência. Limite de referência de 8% (Resolução do Senado nº 9/1992), informado e a conferir.",
        "- ITBI (municipal): lei do município onde se situa o imóvel, alíquota, base e vigência.",
        "- ISS (municipal): lei do município, item da lista de serviços, alíquota e vigência. Limites de referência de 2% a 5% (LC nº 116/2003), informados e a conferir.",
        "- Exceções por mercadoria, operação interestadual e benefício fiscal não estão modeladas.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    rows = load_seed_rows()
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "evidence" / "ops" / f"aliquotas-homologacao-{stamp}.md"
    out.write_text(build_report(rows, stamp), encoding="utf-8", newline="\n")
    homologated = sum(1 for row in rows if not gaps_of(row))
    print(f"versoes={len(rows)} homologadas={homologated} -> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
