# ruff: noqa: E501  (long Portuguese report sentences)
"""Report what is missing before each seeded tax rate counts as homologated.

Read only and offline. It reads the seed rows of alembic/versions/0109_tax_rate_versions.py and
applies sirta_api.domain.tax_rates.homologation_gaps to each one. It does not connect to any
database and never changes a rate or a status. It writes evidence/ops/aliquotas-homologacao-<date>.md.

Usage: python tools/ops/tax-rates-audit.py
"""

from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sirta_api.domain.tax_rates import homologation_gaps  # noqa: E402

MIGRATION = ROOT / "alembic" / "versions" / "0109_tax_rate_versions.py"


def load_seed_rows(path: Path = MIGRATION) -> list[dict]:
    spec = importlib.util.spec_from_file_location("tax_rate_versions_seed", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module._rows()


def gaps_of(row: dict) -> list[str]:
    return homologation_gaps(
        status=row["status"],
        legal_basis=row["legal_basis"],
        official_url=row["official_url"],
        validated_by=row["validated_by"],
        valid_from=row["valid_from"],
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
        "migração `0109_tax_rate_versions`. Nenhuma alíquota ou status foi alterado.",
        "",
        "Critério de homologação: status `VALIDADO` e, ao mesmo tempo, fundamento legal, URL oficial da "
        "legislação, responsável pela validação e início da vigência conhecido. Percentual lido de "
        "uma imagem não atende a nenhum desses itens.",
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
    lines += ["| Imposto | Alíquota (%) | Status | Lacunas |", "| --- | ---: | --- | --- |"]
    for row, gaps in audited:
        if row["tax"] != "ICMS":
            lines.append(
                f"| {row['tax']} | {row['rate']} | {row['status']} | {'; '.join(gaps) or 'nenhuma'} |"
            )
    lines += [
        "",
        "## O que falta informar",
        "",
        "- AC: URL oficial (legis.ac.gov.br) das duas versões, início legal da alíquota de 17% e dispositivo exato.",
        "- 26 UFs: lei ou decreto da alíquota modal, início da vigência, URL oficial e responsável pela validação, uma UF por vez.",
        "- ITCD, ITBI e ISS: legislação aplicável por UF ou município. A alíquota única de 6%, 3% e 5% veio do requisito do Simulador.",
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
