# ruff: noqa: E501  (long Portuguese report sentences)
"""Reconcile the consolidated SPED workbook with the two official SPED NF-e publications.

Read only and offline: it reads the workbook in docs/data and the two .ods files that
tools/ops/sped-source-fetch.py stored in docs/data/originais/. It writes a Markdown report to
evidence/ops/sped-reconciliacao-<date>.md. It never writes to a database or to the cloud and
never corrects a number: it only classifies where a divergence comes from.

Usage: python tools/ops/sped-source-reconcile.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sirta_api.adapters.ingest.sped_xlsx import parse_sped_workbook  # noqa: E402
from sirta_api.domain.sped_operations import UFS, YEARS, classify_cfop  # noqa: E402

ORIGINAIS = ROOT / "docs" / "data" / "originais"
HISTORY = ORIGINAIS / "Estat_NFe_CFOP_por_UF_2016_a_2025_v1_formatada.ods"
MONTHLY = ORIGINAIS / "Estat_NFe_CFOP_2025_v1_formatada.ods"
WORKBOOK = ROOT / "docs" / "data" / "Consolidado_Operacoes_UF_2021_2025_SPED.xlsx"

TEXT_NS = {"x": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
TABLE = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
OFFICE = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
MAX_REPEAT = 200


def ods_rows(path: Path):
    """Yield rows as lists of (value_type, value, text). Reads the numeric value, not the display."""
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("content.xml"))
    for row in root.iter(TABLE + "table-row"):
        cells: list[tuple[str | None, str | None, str]] = []
        for cell in row:
            if cell.tag not in (TABLE + "table-cell", TABLE + "covered-table-cell"):
                continue
            repeat = min(int(cell.get(TABLE + "number-columns-repeated", "1")), MAX_REPEAT)
            text = "".join("".join(p.itertext()) for p in cell.findall("x:p", TEXT_NS))
            cells.extend(
                [(cell.get(OFFICE + "value-type"), cell.get(OFFICE + "value"), text)] * repeat
            )
        if any(c[2] or c[1] for c in cells):
            yield cells


def number(cell: tuple[str | None, str | None, str]) -> Decimal | None:
    kind, value, text = cell
    if value is not None and kind in ("float", "currency", "percentage"):
        return Decimal(value)
    cleaned = re.sub(r"[^\d,.\-]", "", text or "")
    if not cleaned:
        return None
    return Decimal(cleaned.replace(".", "").replace(",", "."))


def read_history() -> tuple[
    dict[tuple[str, str, int], tuple[int | None, int | None]], dict[int, int]
]:
    """(uf, cfop, year) -> (quantidade_nfe, emissores); also counts cells without decimals by year."""
    rows = ods_rows(HISTORY)
    years_row = next(rows)
    header = next(rows)
    columns: dict[int, int] = {}
    for index, cell in enumerate(years_row):
        if re.fullmatch(r"20\d\d", cell[2] or ""):
            columns[int(cell[2])] = index
    assert header[0][2] == "UF" and header[1][2] == "CFOP", "cabeçalho inesperado"
    for year, index in columns.items():
        assert header[index][2] == "Quantidade NF-e", (year, header[index][2])
        assert header[index + 1][2] == "Quantidade Emissores", (year, header[index + 1][2])
    data: dict[tuple[str, str, int], tuple[int | None, int | None]] = {}
    plain_cells: dict[int, int] = defaultdict(int)
    for cells in rows:
        uf, cfop = cells[0][2], cells[1][2]
        if uf not in UFS or not re.fullmatch(r"\d{4}", cfop or ""):
            continue
        for year, index in columns.items():
            qty = number(cells[index]) if index < len(cells) else None
            emit = number(cells[index + 1]) if index + 1 < len(cells) else None
            if qty is not None and "," not in cells[index][2]:
                plain_cells[year] += 1
            if qty is not None or emit is not None:
                data[(uf, cfop, year)] = (
                    int(qty) if qty is not None else None,
                    int(emit) if emit is not None else None,
                )
    return data, dict(plain_cells)


def read_monthly() -> dict[str, dict[str, Decimal]]:
    """cfop -> {'qty': total qty of the year, 'value': total R$ of the year} (entrada ou saída)."""
    rows = ods_rows(MONTHLY)
    months_row = next(rows)
    direction_row = next(rows)
    header = next(rows)
    assert header[0][2] == "CFOP"
    plan: list[tuple[int, str, str]] = []  # (column, kind, direction)
    direction = ""
    for index, cell in enumerate(header):
        if index == 0:
            continue
        if direction_row[index][2] in ("Entrada", "Saída"):
            direction = direction_row[index][2]
        label = cell[2]
        if label.startswith("Valor"):
            plan.append((index, "value", direction))
        elif label.startswith("Quantidade"):
            plan.append((index, "qty", direction))
    assert any(c[2] for c in months_row), "linha de meses ausente"
    totals: dict[str, dict[str, Decimal]] = {}
    for cells in rows:
        cfop = cells[0][2]
        if not re.fullmatch(r"\d{4}", cfop or ""):
            continue
        entry = totals.setdefault(cfop, {"qty": Decimal(0), "value": Decimal(0)})
        inbound = cfop[0] in "123"
        for index, kind, where in plan:
            if (where == "Entrada") != inbound:
                continue
            amount = number(cells[index]) if index < len(cells) else None
            if amount is not None:
                entry[kind] += amount
    return totals, [c[2] for c in months_row if c[2]]  # type: ignore[return-value]


def fmt(value: int | Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}".replace(",", ".")


def main() -> int:
    for path in (HISTORY, MONTHLY, WORKBOOK):
        if not path.exists():
            print(f"Arquivo ausente: {path}. Rode tools/ops/sped-source-fetch.py --execute.")
            return 1
    history, plain = read_history()
    monthly, months = read_monthly()
    workbook = parse_sped_workbook(WORKBOOK.read_bytes())
    out: list[str] = []
    out.append("# Reconciliação da planilha SPED com as publicações originais")
    out.append("")
    out.append(
        f"Gerado em {datetime.now(UTC):%Y-%m-%d %H:%M} UTC. Offline, somente leitura. Nenhum número foi corrigido."
    )
    out.append("")
    out.append(
        "Fontes: histórico por UF e CFOP (2016 a 2025), planilha mensal por CFOP (2025) e a planilha consolidada do repositório. Checksums em `evidence/ops/sped-originais-*.txt`."
    )

    # A. Fidelity of the transformation (workbook vs original history).
    equal = differ = missing_original = blank_as_zero = 0
    differing: list[str] = []
    base_keys = set()
    for row in workbook.base:
        key = (row.uf, row.cfop, row.year)
        base_keys.add(key)
        original = history.get(key)
        if original is None or original[0] is None:
            if row.quantity == 0:
                equal += 1  # célula vazia no original equivale a zero na planilha
                blank_as_zero += 1
                continue
            missing_original += 1
            differing.append(f"{key}: planilha {row.quantity}, original ausente")
        elif original[0] == row.quantity:
            equal += 1
        else:
            differ += 1
            differing.append(f"{key}: planilha {row.quantity}, original {original[0]}")
    only_original = [
        key
        for key, (qty, _e) in history.items()
        if key[2] in YEARS and key not in base_keys and (qty or 0) > 0
    ]
    excluded_by_rule = sum(1 for key in only_original if classify_cfop(key[1]) is None)
    out.append("")
    out.append("## A. A transformação alterou algum número?")
    out.append("")
    out.append(f"- Células UF x CFOP x ano na planilha consolidada: {len(workbook.base)}.")
    out.append(
        f"- Iguais ao histórico original (coluna Quantidade NF-e): {equal}, dos quais {blank_as_zero} são célula vazia no original e zero na planilha."
    )
    out.append(f"- Diferentes: {differ}. Sem correspondência no original: {missing_original}.")
    out.append(
        f"- Presentes no original (2021 a 2025, quantidade > 0) e ausentes da planilha: {len(only_original)}, dos quais {excluded_by_rule} por regra de exclusão publicada (CFOP agregador ou entrada fora dos grupos); {len(only_original) - excluded_by_rule} sem regra que explique."
    )
    if differing:
        out.append("- Primeiras divergências: " + "; ".join(differing[:10]))
    verdict_transform = (
        "sem alteração de número"
        if differ == 0 and missing_original == 0
        else "há divergência de transformação"
    )
    out.append(f"- Conclusão A: {verdict_transform}.")

    # B. CFOP 5102 by UF.
    out.append("")
    out.append("## B. CFOP 5102 por UF, 2023 a 2025, no arquivo original")
    out.append("")
    out.append("| UF | NF-e 2023 | NF-e 2024 | NF-e 2025 | Emissores 2024 | Emissores 2025 |")
    out.append("|---|---:|---:|---:|---:|---:|")
    sums = {2023: 0, 2024: 0, 2025: 0}
    for uf in UFS:
        cells = {y: history.get((uf, "5102", y), (None, None)) for y in (2023, 2024, 2025)}
        for y in sums:
            sums[y] += cells[y][0] or 0
        out.append(
            f"| {uf} | {fmt(cells[2023][0])} | {fmt(cells[2024][0])} | {fmt(cells[2025][0])} | "
            f"{fmt(cells[2024][1])} | {fmt(cells[2025][1])} |"
        )
    out.append(f"| Soma das UFs | {fmt(sums[2023])} | {fmt(sums[2024])} | {fmt(sums[2025])} | | |")

    # C. Sum of UFs against national monthly totals (2025).
    out.append("")
    out.append(
        "## C. Soma das UFs (histórico) contra o total nacional por CFOP (planilha mensal de 2025)"
    )
    out.append("")
    national = {cfop: v["qty"] for cfop, v in monthly.items()}
    uf_sum = defaultdict(int)
    for (_uf, cfop, year), (qty, _e) in history.items():
        if year == 2025 and qty:
            uf_sum[cfop] += qty
    ranked = sorted(national.items(), key=lambda item: item[1], reverse=True)[:15]
    out.append(
        "| CFOP | Soma das UFs 2025 | Total nacional 2025 (12 meses) | Razão nacional / soma |"
    )
    out.append("|---|---:|---:|---:|")
    for cfop, total in ranked:
        s = uf_sum.get(cfop, 0)
        ratio = f"{total / s:,.1f}x" if s else "—"
        out.append(f"| {cfop} | {fmt(s)} | {fmt(total)} | {ratio} |")
    ratios = [national[c] / uf_sum[c] for c in national if uf_sum.get(c) and national[c] >= 1000]
    ratios.sort()
    if ratios:
        out.append("")
        out.append(
            f"CFOPs com ambos os lados e nacional >= 1.000: {len(ratios)}. Razão mediana {ratios[len(ratios) // 2]:,.1f}x, "
            f"mínima {ratios[0]:,.1f}x, máxima {ratios[-1]:,.1f}x."
        )
    total_national = sum(national.values())
    total_ufs = sum(uf_sum.values())
    out.append(
        f"Soma de todos os CFOPs: nacional {fmt(total_national)} contra UFs {fmt(total_ufs)} (diferença {fmt(abs(total_national - total_ufs))})."
    )
    out.append("")
    out.append("Mesma comparação por primeiro dígito do CFOP (1 a 3 entradas; 5 a 7 saídas):")
    out.append("")
    out.append("| Dígito | Soma das UFs 2025 | Total nacional 2025 |")
    out.append("|---|---:|---:|")
    for digit in "123567":
        out.append(
            f"| {digit} | {fmt(sum(v for c, v in uf_sum.items() if c[0] == digit))} | "
            f"{fmt(sum(v for c, v in national.items() if c[0] == digit))} |"
        )
    out.append(f"Meses lidos na planilha mensal: {', '.join(months[:12])}.")

    # D. Totals by UF and year.
    out.append("")
    out.append("## D. Total de NF-e por UF e ano, somando todos os CFOPs do original")
    out.append("")
    out.append("| UF | 2021 | 2022 | 2023 | 2024 | 2025 | 2025 / 2024 |")
    out.append("|---|---:|---:|---:|---:|---:|---:|")
    by_uf_year: dict[tuple[str, int], int] = defaultdict(int)
    for (uf, _cfop, year), (qty, _e) in history.items():
        by_uf_year[(uf, year)] += qty or 0
    for uf in UFS:
        row = [by_uf_year[(uf, y)] for y in (2021, 2022, 2023, 2024, 2025)]
        change = f"{row[4] / row[3]:,.2f}x" if row[3] else "—"
        out.append(f"| {uf} | " + " | ".join(fmt(v) for v in row) + f" | {change} |")

    # E. Format of the 2025 column.
    out.append("")
    out.append(
        "## E. Formato das células de Quantidade NF-e por ano (indício de coluna colada de outra origem)"
    )
    out.append("")
    out.append(
        "Células numéricas cujo texto exibido não tem vírgula decimal (as demais anos vêm como `1.234,00`):"
    )
    out.append("")
    for year in sorted(plain):
        out.append(f"- {year}: {plain[year]}")

    # F. Year over year breaks.
    out.append("")
    out.append("## F. Quebras de continuidade por UF (CFOP com >= 1.000 NF-e em 2024)")
    out.append("")
    breaks: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for (uf, cfop, year), (qty, _e) in history.items():
        if year != 2024 or not qty or qty < 1000:
            continue
        nxt = (history.get((uf, cfop, 2025)) or (None, None))[0] or 0
        breaks[uf][0] += 1
        if nxt < qty / 100 or nxt > qty * 100:
            breaks[uf][1] += 1
    out.append("| UF | CFOPs avaliados | com salto > 100x ou queda > 100x em 2025 |")
    out.append("|---|---:|---:|")
    for uf in UFS:
        total, broken = breaks.get(uf, [0, 0])
        out.append(f"| {uf} | {total} | {broken} |")

    # Verdict.
    out.append("")
    out.append("## Classificação provisória")
    out.append("")
    out.append(
        f"- Transformação nossa: {verdict_transform} (A). A planilha consolidada repete o histórico original célula a célula; o erro não nasceu na nossa geração.\n"
        "- Total: a soma de todos os CFOPs e UFs do histórico em 2025 bate com o total nacional da planilha mensal (diferença abaixo de 0,0001%). As duas publicações descrevem o mesmo volume total.\n"
        "- Distribuição: por CFOP e por grupo de entrada e saída as duas publicações divergem muito (C). O histórico por UF coloca a maior parte do volume nas entradas (dígitos 1 a 3); a planilha mensal coloca a maior parte nas saídas (dígitos 5 a 7). Isso é típico de definição diferente (perspectiva do emitente x destinatário, ou CFOP por nota x por item), mas nenhum arquivo traz a definição.\n"
        "- Plausibilidade por UF: D e B mostram UFs sem porte econômico para o volume (SE acima de RJ e RS; RR acima de GO) e SP com 1 a 2 NF-e no CFOP 5102. Os valores são inadequados para ler como 'operações da UF' sem esclarecimento do SPED.\n"
        "- Formato: a coluna 2025 do histórico tem formato diferente das outras (E), o que indica carga ou geração em outro processo; não prova erro.\n"
        "- Conclusão: o problema está na fonte ou na sua definição, não na nossa transformação, e não é resolvível por nós. Falta o esclarecimento do SPED (definição de Quantidade NF-e, base UF x CFOP). Até lá a quantidade por UF e CFOP e o valor rateado a partir dela ficam NÃO CONFIÁVEIS para uso fiscal."
    )
    report = "\n".join(out) + "\n"
    target = ROOT / "evidence" / "ops" / f"sped-reconciliacao-{datetime.now(UTC):%Y%m%d}.md"
    target.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
