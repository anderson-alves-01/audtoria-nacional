"""Synthetic workbook with the same layout as the SPED consolidated file.

No real figure is used here. Numbers come from a fixed formula so reconciliation is exact.
"""

from __future__ import annotations

import io
import zipfile
from collections.abc import Callable
from xml.sax.saxutils import escape

UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]  # fmt: skip
YEARS = [2021, 2022, 2023, 2024, 2025]
OPERATIONS = [
    "Compras",
    "Vendas",
    "Transferências",
    "Doações / bonificações / brindes",
    "Serviços Prestados",
    "Serviços Tomados",
    "Outras Saídas",
]
CFOP_BY_OPERATION = {
    "Compras": "1102",
    "Vendas": "5102",
    "Transferências": "5152",
    "Doações / bonificações / brindes": "5910",
    "Serviços Prestados": "5353",
    "Serviços Tomados": "1353",
    "Outras Saídas": "5949",
}
CONSOLIDATED_LABELS = {
    "Compras": "Compras",
    "Vendas": "Vendas",
    "Transferências": "Transferências",
    "Doações / bonificações / brindes": "Doações*",
    "Serviços Prestados": "Serviços Prestados",
    "Serviços Tomados": "Serviços Tomados",
    "Outras Saídas": "Outras Saídas",
}
SERIE_HEADER = [
    "Ano",
    "UF",
    "Operação",
    "Quantidade de ocorrências",
    "Valor UF estimado (R$)",
    "Qtd. em faixas comparáveis",
    "% em faixas comparáveis",
    "Nº pares UF/CFOP",
    "Qtd. coberta por valor",
]


def quantity(uf: str, year: int, operation: str) -> int:
    return (UFS.index(uf) + 1) * 100 + (year - 2020) * 10 + OPERATIONS.index(operation)


def amount(uf: str, year: int, operation: str) -> float:
    return round(quantity(uf, year, operation) * 10.5, 2)


Cell = str | int | float | None
Row = list[Cell]


def _col(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rest = divmod(index - 1, 26)
        letters = chr(65 + rest) + letters
    return letters


def _sheet_xml(rows: list[tuple[int, Row]]) -> str:
    body = []
    for number, cells in rows:
        parts = []
        for position, value in enumerate(cells):
            ref = f"{_col(position)}{number}"
            if value is None:
                parts.append(f'<x:c r="{ref}"/>')
            elif isinstance(value, str):
                parts.append(
                    f'<x:c r="{ref}" t="inlineStr"><x:is><x:t>{escape(value)}</x:t></x:is></x:c>'
                )
            else:
                parts.append(f'<x:c r="{ref}"><x:v>{value}</x:v></x:c>')
        body.append(f'<x:row r="{number}">{"".join(parts)}</x:row>')
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<x:worksheet xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<x:sheetData>{''.join(body)}</x:sheetData></x:worksheet>"
    )


def _consolidated_formula_cell(ref: str, formula: str, cached: Cell) -> str:
    value = "" if cached is None else f"<x:v>{cached}</x:v>"
    return f'<x:c r="{ref}"><x:f>{escape(formula)}</x:f>{value}</x:c>'


def build_sped_workbook(
    *,
    ufs: list[str] | None = None,
    years: list[int] | None = None,
    mutate_serie: Callable[[list[Row]], None] | None = None,
    mutate_base: Callable[[list[Row]], None] | None = None,
    mutate_consolidated: Callable[[dict[tuple[str, str, str], Cell]], None] | None = None,
    drop_sheet: str | None = None,
    serie_header: list[str] | None = None,
) -> bytes:
    ufs = ufs if ufs is not None else UFS
    years = years if years is not None else YEARS

    serie: list[Row] = []
    for year in years:
        for uf in ufs:
            for operation in OPERATIONS:
                qty = quantity(uf, year, operation)
                value: Cell = amount(uf, year, operation)
                if operation == "Serviços Prestados" and uf == ufs[0]:
                    qty, value = 0, None  # no occurrence: value stays blank, never zero
                serie.append([year, uf, operation, qty, value, 0, 0, 1, qty])
    if mutate_serie:
        mutate_serie(serie)

    base: list[Row] = []
    for uf in ufs:
        for operation in OPERATIONS:
            row: Row = [uf, CFOP_BY_OPERATION[operation], operation]
            for year in years:
                qty = quantity(uf, year, operation)
                if operation == "Serviços Prestados" and uf == ufs[0]:
                    row += [0, 0]
                else:
                    row += [qty, amount(uf, year, operation)]
            base.append(row)
    if mutate_base:
        mutate_base(base)

    totals: dict[tuple[str, str, str], Cell] = {}
    for row in serie:
        key_qty = (str(row[1]), str(row[2]), "qty")
        key_val = (str(row[1]), str(row[2]), "value")
        totals[key_qty] = int(totals.get(key_qty) or 0) + int(row[3] or 0)  # type: ignore[arg-type]
        if isinstance(row[4], int | float):
            totals[key_val] = round(float(totals.get(key_val) or 0) + float(row[4]), 2)  # type: ignore[arg-type]
        else:
            totals.setdefault(key_val, None)
    if mutate_consolidated:
        mutate_consolidated(totals)

    consolidated_rows = []
    header = ["UF"]
    for operation in OPERATIONS:
        label = CONSOLIDATED_LABELS[operation]
        header += [f"{label}\nQtd.", f"{label}\nR$ estimado"]
    for number, cells in (
        (2, ["Consolidado de operações por UF"]),
        (5, ["ATENÇÃO: o valor (R$) por UF é um RATEIO ESTIMADO de totais nacionais."]),
        (8, header),
    ):
        consolidated_rows.append((number, cells))
    sheet1_rows = "".join(
        f'<x:row r="{n}">'
        + "".join(
            f'<x:c r="{_col(i)}{n}" t="inlineStr"><x:is><x:t>{escape(str(v))}</x:t></x:is></x:c>'
            for i, v in enumerate(c)
        )
        + "</x:row>"
        for n, c in consolidated_rows
    )
    line = 9
    for uf in ufs:
        cells = [f'<x:c r="A{line}" t="inlineStr"><x:is><x:t>{uf}</x:t></x:is></x:c>']
        for index, operation in enumerate(OPERATIONS):
            for offset, kind in enumerate(("qty", "value")):
                ref = f"{_col(1 + index * 2 + offset)}{line}"
                formula = f"SUMIFS('Série anual'!$D$7:$D$951,'Série anual'!$B$7:$B$951,$A{line})"
                cells.append(
                    _consolidated_formula_cell(ref, formula, totals.get((uf, operation, kind)))
                )
        sheet1_rows += f'<x:row r="{line}">{"".join(cells)}</x:row>'
        line += 1
    sheet1 = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<x:worksheet xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<x:sheetData>{sheet1_rows}</x:sheetData></x:worksheet>"
    )

    sheet2 = _sheet_xml(
        [(2, ["Série anual por operação"]), (6, serie_header or SERIE_HEADER)]
        + [(7 + i, row) for i, row in enumerate(serie)]
    )
    base_header: Row = ["UF", "CFOP", "Operação"]
    for year in years:
        base_header += [f"{year} Qtd.", f"{year} R$ estimado"]
    sheet3 = _sheet_xml(
        [(2, ["Base por UF e CFOP"]), (6, base_header)]
        + [(7 + i, row) for i, row in enumerate(base)]
    )
    sheet4 = _sheet_xml([(2, ["Fontes, critérios e limitações"])])

    sheets = [
        ("Consolidado UF", sheet1),
        ("Série anual", sheet2),
        ("Base CFOP", sheet3),
        ("Fontes e método", sheet4),
    ]
    sheets = [item for item in sheets if item[0] != drop_sheet]
    workbook = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<x:workbook xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><x:sheets>'
        + "".join(
            f'<x:sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>'
            for i, (name, _xml) in enumerate(sheets, start=1)
        )
        + "</x:sheets></x:workbook>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/'
            f'2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, len(sheets) + 1)
        )
        + "</Relationships>"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", rels)
        for i, (_name, xml) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{i}.xml", xml)
    return buffer.getvalue()
