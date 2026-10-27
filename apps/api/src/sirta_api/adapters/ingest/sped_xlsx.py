"""Reader for the SPED consolidated workbook. Standard library only (zipfile + ElementTree).

Fails closed: a missing sheet, missing column or non numeric figure raises SpedLayoutError.
A blank figure stays None. It is never read as zero.
"""

from __future__ import annotations

import io
import re
import zipfile
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET

from sirta_api.domain.sped_operations import (
    OPERATIONS,
    YEARS,
    SpedBaseRow,
    SpedSerieRow,
    SpedWorkbook,
)

MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
SHEET_SERIE = "Série anual"
SHEET_BASE = "Base CFOP"
SHEET_CONSOLIDATED = "Consolidado UF"
CONSOLIDATED_LABELS = {
    "Compras": "Compras",
    "Vendas": "Vendas",
    "Transferências": "Transferências",
    "Doações": "Doações / bonificações / brindes",
    "Serviços Prestados": "Serviços Prestados",
    "Serviços Tomados": "Serviços Tomados",
    "Outras Saídas": "Outras Saídas",
}


class SpedLayoutError(ValueError):
    pass


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _column_index(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref)
    if letters is None:
        raise SpedLayoutError(f"Referência de célula inválida: {ref!r}.")
    index = 0
    for char in letters.group(0):
        index = index * 26 + (ord(char) - 64)
    return index - 1


def _read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.iter() if _local(node.tag) == "t")
        for item in root
        if _local(item.tag) == "si"
    ]


def _sheet_paths(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        item.get("Id"): item.get("Target", "")
        for item in rels
        if _local(item.tag) == "Relationship"
    }
    paths: dict[str, str] = {}
    for sheet in workbook.iter():
        if _local(sheet.tag) != "sheet":
            continue
        rid = next((value for key, value in sheet.attrib.items() if _local(key) == "id"), None)
        target = targets.get(rid or "")
        name = sheet.get("name")
        if not (name and target):
            continue
        target = target.lstrip("/")
        paths[name] = target if target.startswith("xl/") else f"xl/{target}"
    return paths


def _cell_value(cell: ET.Element, shared: list[str]) -> str | None:
    kind = cell.get("t")
    if kind == "inlineStr":
        text = "".join(node.text or "" for node in cell.iter() if _local(node.tag) == "t")
        return text
    raw = next((node.text for node in cell if _local(node.tag) == "v"), None)
    if raw is None or raw == "":
        return None
    if kind == "s":
        return shared[int(raw)]
    return raw


def _read_rows(
    archive: zipfile.ZipFile, path: str, shared: list[str]
) -> list[tuple[int, dict[int, str | None]]]:
    root = ET.fromstring(archive.read(path))
    rows: list[tuple[int, dict[int, str | None]]] = []
    for row in root.iter():
        if _local(row.tag) != "row":
            continue
        cells: dict[int, str | None] = {}
        for cell in row:
            if _local(cell.tag) == "c" and cell.get("r"):
                cells[_column_index(cell.get("r", ""))] = _cell_value(cell, shared)
        rows.append((int(row.get("r") or 0), cells))
    return rows


def _header(
    rows: list[tuple[int, dict[int, str | None]]], first_cell: str, sheet: str
) -> tuple[int, dict[str, int]]:
    for number, cells in rows:
        if (cells.get(0) or "").strip() == first_cell:
            return number, {
                (text or "").replace("\n", " ").strip(): index
                for index, text in cells.items()
                if text
            }
    raise SpedLayoutError(f"Aba {sheet}: cabeçalho com '{first_cell}' não encontrado.")


def _need(columns: dict[str, int], name: str, sheet: str) -> int:
    if name not in columns:
        raise SpedLayoutError(f"Aba {sheet}: coluna '{name}' ausente.")
    return columns[name]


def _decimal(raw: str | None, where: str) -> Decimal | None:
    if raw is None or raw.strip() == "":
        return None
    try:
        return Decimal(raw.strip())
    except InvalidOperation as exc:
        raise SpedLayoutError(f"Valor não numérico em {where}: {raw!r}.") from exc


def _integer(raw: str | None, where: str, *, required: bool = True) -> int | None:
    value = _decimal(raw, where)
    if value is None:
        if required:
            raise SpedLayoutError(f"Quantidade ausente em {where}.")
        return None
    if value != value.to_integral_value():
        raise SpedLayoutError(f"Valor não numérico inteiro em {where}: {raw!r}.")
    return int(value)


def _money(raw: str | None, where: str) -> Decimal | None:
    value = _decimal(raw, where)
    return None if value is None else value.quantize(Decimal("0.01"))


def parse_sped_workbook(body: bytes) -> SpedWorkbook:
    try:
        archive = zipfile.ZipFile(io.BytesIO(body))
    except zipfile.BadZipFile as exc:
        raise SpedLayoutError("O arquivo não é uma planilha xlsx.") from exc
    with archive:
        if sum(item.file_size for item in archive.infolist()) > MAX_UNCOMPRESSED_BYTES:
            raise SpedLayoutError("A planilha descompactada excede o limite aceito.")
        try:
            paths = _sheet_paths(archive)
            shared = _read_shared_strings(archive)
        except (KeyError, ET.ParseError) as exc:
            raise SpedLayoutError("A estrutura do xlsx está incompleta.") from exc
        for name in (SHEET_CONSOLIDATED, SHEET_SERIE, SHEET_BASE):
            if name not in paths:
                raise SpedLayoutError(f"Aba {name} ausente.")
        try:
            serie = _parse_serie(_read_rows(archive, paths[SHEET_SERIE], shared))
            base = _parse_base(_read_rows(archive, paths[SHEET_BASE], shared))
            consolidated = _parse_consolidated(
                _read_rows(archive, paths[SHEET_CONSOLIDATED], shared)
            )
        except (KeyError, ET.ParseError) as exc:
            raise SpedLayoutError("Não foi possível ler uma das abas do xlsx.") from exc
    return SpedWorkbook(serie=serie, base=base, consolidated=consolidated)


def _parse_serie(rows: list[tuple[int, dict[int, str | None]]]) -> list[SpedSerieRow]:
    header_row, columns = _header(rows, "Ano", SHEET_SERIE)
    c_year = _need(columns, "Ano", SHEET_SERIE)
    c_uf = _need(columns, "UF", SHEET_SERIE)
    c_op = _need(columns, "Operação", SHEET_SERIE)
    c_qty = _need(columns, "Quantidade de ocorrências", SHEET_SERIE)
    c_val = _need(columns, "Valor UF estimado (R$)", SHEET_SERIE)
    c_cmp = _need(columns, "Qtd. em faixas comparáveis", SHEET_SERIE)
    c_share = _need(columns, "% em faixas comparáveis", SHEET_SERIE)
    c_pairs = _need(columns, "Nº pares UF/CFOP", SHEET_SERIE)
    c_cov = _need(columns, "Qtd. coberta por valor", SHEET_SERIE)
    out: list[SpedSerieRow] = []
    for number, cells in rows:
        if number <= header_row or not (cells.get(c_uf) or "").strip():
            continue
        where = f"Série anual linha {number}"
        year = _integer(cells.get(c_year), f"{where} (ano)")
        out.append(
            SpedSerieRow(
                year=int(year or 0),
                uf=(cells.get(c_uf) or "").strip(),
                operation=(cells.get(c_op) or "").strip(),
                quantity=int(_integer(cells.get(c_qty), f"{where} (quantidade)") or 0),
                estimated_value=_money(cells.get(c_val), f"{where} (valor)"),
                comparable_quantity=_integer(cells.get(c_cmp), where, required=False),
                comparable_share=_decimal(cells.get(c_share), where),
                cfop_pairs=_integer(cells.get(c_pairs), where, required=False),
                covered_quantity=_integer(cells.get(c_cov), where, required=False),
            )
        )
    return out


def _parse_base(rows: list[tuple[int, dict[int, str | None]]]) -> list[SpedBaseRow]:
    header_row, columns = _header(rows, "UF", SHEET_BASE)
    c_uf = _need(columns, "UF", SHEET_BASE)
    c_cfop = _need(columns, "CFOP", SHEET_BASE)
    c_op = _need(columns, "Operação", SHEET_BASE)
    year_columns: list[tuple[int, int, int]] = []
    for year in YEARS:
        year_columns.append(
            (
                year,
                _need(columns, f"{year} Qtd.", SHEET_BASE),
                _need(columns, f"{year} R$ estimado", SHEET_BASE),
            )
        )
    out: list[SpedBaseRow] = []
    for number, cells in rows:
        if number <= header_row or not (cells.get(c_uf) or "").strip():
            continue
        where = f"Base CFOP linha {number}"
        for year, c_qty, c_val in year_columns:
            out.append(
                SpedBaseRow(
                    uf=(cells.get(c_uf) or "").strip(),
                    cfop=(cells.get(c_cfop) or "").strip(),
                    operation=(cells.get(c_op) or "").strip(),
                    year=year,
                    quantity=int(_integer(cells.get(c_qty), f"{where} {year} (quantidade)") or 0),
                    estimated_value=_money(cells.get(c_val), f"{where} {year} (valor)"),
                )
            )
    return out


def _parse_consolidated(
    rows: list[tuple[int, dict[int, str | None]]],
) -> dict[tuple[str, str, str], Decimal | None]:
    header_row, columns = _header(rows, "UF", SHEET_CONSOLIDATED)
    mapping: dict[int, tuple[str, str]] = {}
    for text, index in columns.items():
        label = text.replace(" Qtd.", "").replace(" R$ estimado", "").rstrip("*").strip()
        if text.endswith(" Qtd.") and label in CONSOLIDATED_LABELS:
            mapping[index] = (CONSOLIDATED_LABELS[label], "qty")
        elif text.endswith(" R$ estimado") and label in CONSOLIDATED_LABELS:
            mapping[index] = (CONSOLIDATED_LABELS[label], "value")
    expected = len(OPERATIONS) * 2
    if len(mapping) != expected:
        raise SpedLayoutError(
            f"Aba {SHEET_CONSOLIDATED}: esperadas {expected} colunas de operação, "
            f"encontradas {len(mapping)}."
        )
    out: dict[tuple[str, str, str], Decimal | None] = {}
    for number, cells in rows:
        uf = (cells.get(0) or "").strip()
        if number <= header_row or not uf:
            continue
        for index, (operation, kind) in mapping.items():
            out[(uf, operation, kind)] = _decimal(
                cells.get(index), f"Consolidado UF linha {number}"
            )
    return out
