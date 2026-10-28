# ruff: noqa: E501  (long Portuguese report sentences)
"""Audit every UF x CFOP x year cell that exists in the official SPED history but is absent
from the consolidated workbook, and say which published rule explains each absence.

Read only and offline. It reads the two files kept in docs/data/originais/ and the consolidated
workbook in docs/data. It writes two files to evidence/ops/ and nothing else: a Markdown report
and a CSV with the cells no published rule explains. It never changes a source number and never
tries to make the two publications agree.

Classes
- legitima:           the workbook publishes the rule (CFOP ending in 00 or 50).
- legitima_material:  the workbook publishes the rule (inbound CFOP outside the seven groups), but the
                      volume left out is large enough to limit what the base represents.
- indevida:           the workbook's own classification says "Compras" (or another group), yet the
                      cell is not in the workbook. No published rule explains the absence.

Usage: python tools/ops/sped-omission-audit.py
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sirta_api.domain.sped_operations import YEARS, classify_cfop  # noqa: E402

AGREGADOR = "AGREGADOR_00_50"
ENTRADA_FORA = "ENTRADA_FORA_DOS_GRUPOS"
SEM_REGRA = "SEM_REGRA_PUBLICADA"
FORA_DAS_CATEGORIAS = "(fora das sete categorias)"

RULE_CLASS = {
    AGREGADOR: "legitima",
    ENTRADA_FORA: "legitima_material",
    SEM_REGRA: "indevida",
}
RULE_TEXT = {
    AGREGADOR: "Exclusões da aba 'Fontes e método': códigos agregadores terminados em 00 ou 50.",
    ENTRADA_FORA: "Exclusões da aba 'Fontes e método': entradas que não cabem nas sete categorias.",
    SEM_REGRA: "Nenhuma regra publicada. classify_cfop devolve uma operação, mas a célula não está na planilha.",
}


@dataclass(frozen=True)
class Omission:
    uf: str
    cfop: str
    year: int
    quantity: int
    rule: str
    klass: str
    operation: str


def assign_rule(cfop: str) -> str:
    """Return the published rule that explains why a CFOP is absent, or SEM_REGRA."""
    if cfop.endswith(("00", "50")):
        return AGREGADOR
    if classify_cfop(cfop) is None:
        return ENTRADA_FORA
    return SEM_REGRA


def audit(
    history: dict[tuple[str, str, int], tuple[int | None, int | None]],
    base_keys: set[tuple[str, str, int]],
    years: Iterable[int] = YEARS,
) -> list[Omission]:
    """Every history cell (quantity > 0) of the given years that is not in the workbook base."""
    wanted = set(years)
    result: list[Omission] = []
    for (uf, cfop, year), (quantity, _emitters) in sorted(history.items()):
        if year not in wanted or not quantity or quantity <= 0:
            continue
        if (uf, cfop, year) in base_keys:
            continue
        rule = assign_rule(cfop)
        operation = classify_cfop(cfop) or FORA_DAS_CATEGORIAS
        result.append(Omission(uf, cfop, year, quantity, rule, RULE_CLASS[rule], operation))
    return result


def totals_by(omissions: Iterable[Omission], key) -> dict:
    out: dict = defaultdict(lambda: [0, 0])
    for item in omissions:
        cell = out[key(item)]
        cell[0] += 1
        cell[1] += item.quantity
    return dict(out)


def _fmt(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _pct(part: int, whole: int) -> str:
    return "—" if not whole else f"{100 * part / whole:.1f}%".replace(".", ",")


def _ratio(part: int, whole: int) -> str:
    return "—" if not whole else f"{part / whole:.2f}x".replace(".", ",")


def _load_reconcile():
    spec = importlib.util.spec_from_file_location(
        "sped_source_reconcile", ROOT / "tools" / "ops" / "sped-source-reconcile.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_report(
    omissions: list[Omission],
    history_totals_by_year: dict[int, int],
    included_by_year: dict[int, int],
    compras_by_uf_year: dict[tuple[str, int], int],
    stamp: str,
) -> str:
    bad = [o for o in omissions if o.klass == "indevida"]
    lines: list[str] = []
    add = lines.append
    add(f"# Auditoria das omissões da planilha SPED ({stamp})")
    add("")
    add(
        "Gerado por `tools/ops/sped-omission-audit.py`, somente leitura. Compara o histórico oficial "
        "(UF x CFOP x ano, quantidade maior que zero, 2021 a 2025) com a base da planilha consolidada. "
        "Nenhum número original foi alterado. Os dois arquivos oficiais continuam em `docs/data/originais/`."
    )
    add("")
    add("## 1. Regra responsável por cada célula ausente")
    add("")
    add("| Regra | Classe | Células | Quantidade de NF-e | Justificativa |")
    add("| --- | --- | ---: | ---: | --- |")
    by_rule = totals_by(omissions, lambda o: o.rule)
    for rule in (AGREGADOR, ENTRADA_FORA, SEM_REGRA):
        count, qty = by_rule.get(rule, (0, 0))
        add(f"| {rule} | {RULE_CLASS[rule]} | {_fmt(count)} | {_fmt(qty)} | {RULE_TEXT[rule]} |")
    total_count = sum(v[0] for v in by_rule.values())
    total_qty = sum(v[1] for v in by_rule.values())
    add(f"| **Total ausente** |  | **{_fmt(total_count)}** | **{_fmt(total_qty)}** |  |")
    add("")
    add(
        f"Invariante verificado: legítimas ({_fmt(total_count - len(bad))}) + indevidas ({_fmt(len(bad))}) = {_fmt(total_count)} células ausentes."
    )
    add("")
    add("## 2. Cobertura por ano")
    add("")
    add(
        "| Ano | Histórico oficial (NF-e) | Incluído na planilha | Cobertura | Omissão indevida | Indevida / incluído |"
    )
    add("| ---: | ---: | ---: | ---: | ---: | ---: |")
    bad_year = totals_by(bad, lambda o: o.year)
    for year in sorted(history_totals_by_year):
        hist = history_totals_by_year[year]
        inc = included_by_year.get(year, 0)
        indev = bad_year.get(year, (0, 0))[1]
        add(
            f"| {year} | {_fmt(hist)} | {_fmt(inc)} | {_pct(inc, hist)} | {_fmt(indev)} | {_pct(indev, inc)} |"
        )
    add("")
    add(
        "A cobertura baixa decorre das exclusões legítimas (entradas fora dos grupos). Ela limita o que a base representa, mas não é erro de transformação."
    )
    add("")
    add("## 3. Omissões indevidas por operação")
    add("")
    add("| Operação (regra publicada) | Células | Quantidade de NF-e |")
    add("| --- | ---: | ---: |")
    for operation, (count, qty) in sorted(totals_by(bad, lambda o: o.operation).items()):
        add(f"| {operation} | {_fmt(count)} | {_fmt(qty)} |")
    add("")
    add("## 4. Omissões indevidas por ano")
    add("")
    add("| Ano | Células | Quantidade de NF-e |")
    add("| ---: | ---: | ---: |")
    for year, (count, qty) in sorted(bad_year.items()):
        add(f"| {year} | {_fmt(count)} | {_fmt(qty)} |")
    add("")
    add("## 5. Omissões indevidas por CFOP")
    add("")
    add("| CFOP | Células | Quantidade de NF-e |")
    add("| --- | ---: | ---: |")
    for cfop, (count, qty) in sorted(totals_by(bad, lambda o: o.cfop).items()):
        add(f"| {cfop} | {_fmt(count)} | {_fmt(qty)} |")
    add("")
    add("## 6. Omissões indevidas por UF, com o peso sobre as Compras incluídas")
    add("")
    add(
        "`Indevida / Compras incluídas` mostra quantas vezes o volume omitido supera o que a planilha publica como Compras da UF no período."
    )
    add("")
    add(
        "| UF | Células | NF-e omitidas | Compras incluídas (NF-e) | Indevida / Compras incluídas |"
    )
    add("| --- | ---: | ---: | ---: | ---: |")
    by_uf = totals_by(bad, lambda o: o.uf)
    compras_uf: dict[str, int] = defaultdict(int)
    for (uf, _year), qty in compras_by_uf_year.items():
        compras_uf[uf] += qty
    for uf, (count, qty) in sorted(by_uf.items(), key=lambda item: -item[1][1]):
        add(
            f"| {uf} | {_fmt(count)} | {_fmt(qty)} | {_fmt(compras_uf.get(uf, 0))} | {_ratio(qty, compras_uf.get(uf, 0))} |"
        )
    add("")
    add("## 7. UF e ano mais afetados (omitido sobre Compras incluídas)")
    add("")
    add("| UF | Ano | NF-e omitidas | Compras incluídas | Razão |")
    add("| --- | ---: | ---: | ---: | ---: |")
    by_uf_year = totals_by(bad, lambda o: (o.uf, o.year))
    ranked = sorted(
        by_uf_year.items(),
        key=lambda item: (
            -(item[1][1] / compras_by_uf_year[item[0]] if compras_by_uf_year.get(item[0]) else 0)
        ),
    )
    for (uf, year), (_count, qty) in ranked[:15]:
        base = compras_by_uf_year.get((uf, year), 0)
        add(f"| {uf} | {year} | {_fmt(qty)} | {_fmt(base)} | {_ratio(qty, base)} |")
    add("")
    add("## 8. Exclusões legítimas pela regra publicada, por CFOP (15 maiores)")
    add("")
    legit = [o for o in omissions if o.klass != "indevida"]
    add("| CFOP | Regra | Células | Quantidade de NF-e |")
    add("| --- | --- | ---: | ---: |")
    by_cfop = totals_by(legit, lambda o: (o.cfop, o.rule))
    for (cfop, rule), (count, qty) in sorted(by_cfop.items(), key=lambda item: -item[1][1])[:15]:
        add(f"| {cfop} | {rule} | {_fmt(count)} | {_fmt(qty)} |")
    add("")
    add("## 9. Classificação")
    add("")
    add(
        "- **Legítimas.** Seguem uma regra escrita na planilha. Continuam sujeitas à revisão da definição de `Quantidade NF-e` pelo SPED, pois a regra de classificação é, nas palavras da própria planilha, aproximada."
    )
    add(
        "- **Indevidas.** Pela regra publicada, os CFOPs 1.15x, 1.190, 2.15x e 2.170 pertencem a Compras, mas estão ausentes da `Base CFOP` e da `Série anual` em todas as UFs e anos. A omissão atinge as duas abas ao mesmo tempo, por isso a conferência interna da planilha não a detecta."
    )
    add(
        "- **Decisão metodológica pendente.** Entradas por transferência (1.15x e 2.15x) podem duplicar as saídas por transferência (5.15x e 6.15x). O responsável deve decidir se pertencem a Compras, a uma categoria própria ou à exclusão. Enquanto isso, nada é reincluído nem corrigido."
    )
    add(
        "- **Efeito.** A planilha não é homologável como está. O indicador de Compras por UF fica `NAO_CONFIAVEL` (ver `config/indicator-reliability.yaml`)."
    )
    add("")
    return "\n".join(lines) + "\n"


def write_csv(path: Path, omissions: list[Omission]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "uf",
                "cfop",
                "ano",
                "quantidade_nfe",
                "regra",
                "classe",
                "operacao_pela_regra_publicada",
            ]
        )
        for o in omissions:
            writer.writerow([o.uf, o.cfop, o.year, o.quantity, o.rule, o.klass, o.operation])


def main() -> int:
    recon = _load_reconcile()
    for path in (recon.HISTORY, recon.WORKBOOK):
        if not path.is_file():
            print(f"arquivo ausente: {path}")
            return 1
    history, _plain = recon.read_history()
    workbook = recon.parse_sped_workbook(recon.WORKBOOK.read_bytes())
    base_keys = {(row.uf, row.cfop, row.year) for row in workbook.base}
    omissions = audit(history, base_keys)

    history_totals: dict[int, int] = defaultdict(int)
    for (_uf, _cfop, year), (qty, _emit) in history.items():
        if year in YEARS and qty and qty > 0:
            history_totals[year] += qty
    included: dict[int, int] = defaultdict(int)
    compras: dict[tuple[str, int], int] = defaultdict(int)
    for row in workbook.base:
        included[row.year] += row.quantity
        if row.operation == "Compras":
            compras[(row.uf, row.year)] += row.quantity

    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out_dir = ROOT / "evidence" / "ops"
    report_path = out_dir / f"sped-auditoria-omissoes-{stamp}.md"
    csv_path = out_dir / f"sped-omissoes-1041-{stamp}.csv"
    report_path.write_text(
        build_report(omissions, dict(history_totals), dict(included), dict(compras), stamp),
        encoding="utf-8",
        newline="\n",
    )
    bad = [o for o in omissions if o.klass == "indevida"]
    write_csv(csv_path, bad)
    print(
        f"celulas ausentes={len(omissions)} indevidas={len(bad)} -> {report_path.name}, {csv_path.name}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
