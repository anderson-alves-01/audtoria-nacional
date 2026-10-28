# ruff: noqa: E501  (OOXML literals)
"""Minimal streaming XLSX writer and reader (standard library only).

``openpyxl`` is not a project dependency. The writer streams rows to the ZIP, so a large sheet never
sits in memory. Numbers are written as numbers (Excel keeps about 15 significant digits: the
companion CSVs are the exact copies). Text is written inline, so identifiers such as NCM, CFOP and
access keys stay text with their leading zeros.
"""

from __future__ import annotations

import zipfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

EXCEL_MAX_ROWS = 1_048_576
EXCEL_MAX_COLS = 16_384
SIGNIFICANT_DIGITS = 15

STYLE_DEFAULT, STYLE_HEADER, STYLE_MONEY, STYLE_INT, STYLE_WRAP, STYLE_TITLE = 0, 1, 2, 3, 4, 5

_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


class SheetTooLarge(ValueError):
    """The sheet would pass Excel's row limit. The caller must choose a coarser grain."""


@dataclass(frozen=True)
class Money:
    """Amount in integer cents. Written as a number with two decimals."""

    cents: int

    def text(self) -> str:
        sign = "-" if self.cents < 0 else ""
        whole, frac = divmod(abs(self.cents), 100)
        return f"{sign}{whole}.{frac:02d}"


def column_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


_STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="{_NS}">
<numFmts count="1"><numFmt numFmtId="164" formatCode="#,##0.00"/></numFmts>
<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><name val="Calibri"/></font>
<font><b/><sz val="14"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFD9E1F2"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="6">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="3" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs>
</styleSheet>"""


class SheetWriter:
    def __init__(self, stream, widths: list[float] | None, freeze_rows: int) -> None:
        self._stream = stream
        self.rows = 0
        self._write(
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<worksheet xmlns="{_NS}" xmlns:r="{_REL}">'
        )
        if freeze_rows:
            self._write(
                f'<sheetViews><sheetView workbookViewId="0"><pane ySplit="{freeze_rows}" '
                f'topLeftCell="A{freeze_rows + 1}" activePane="bottomLeft" state="frozen"/>'
                f"</sheetView></sheetViews>"
            )
        if widths:
            cols = "".join(
                f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>'
                for i, w in enumerate(widths)
            )
            self._write(f"<cols>{cols}</cols>")
        self._write("<sheetData>")

    def _write(self, text: str) -> None:
        self._stream.write(text.encode("utf-8"))

    def write_row(self, values: Iterable[object], *, style: int | None = None) -> None:
        self.rows += 1
        if self.rows > EXCEL_MAX_ROWS:
            raise SheetTooLarge(f"mais de {EXCEL_MAX_ROWS} linhas")
        cells: list[str] = []
        for position, value in enumerate(values):
            if position >= EXCEL_MAX_COLS:
                raise SheetTooLarge("colunas acima do limite do Excel")
            ref = f"{column_letter(position)}{self.rows}"
            cell = self._cell(ref, value, style)
            if cell:
                cells.append(cell)
        self._write(f'<row r="{self.rows}">{"".join(cells)}</row>')

    @staticmethod
    def _text_cell(ref: str, text: str, style: int | None) -> str:
        s = f' s="{style}"' if style else ""
        preserve = ' xml:space="preserve"' if text != text.strip() or "\n" in text else ""
        return f'<c r="{ref}" t="inlineStr"{s}><is><t{preserve}>{escape(text)}</t></is></c>'

    def _cell(self, ref: str, value: object, row_style: int | None) -> str:
        if value is None or value == "":
            return ""
        if isinstance(value, Money):
            return f'<c r="{ref}" s="{STYLE_MONEY}"><v>{value.text()}</v></c>'
        if isinstance(value, bool):
            return self._text_cell(ref, "SIM" if value else "NAO", row_style)
        if isinstance(value, int):
            if len(str(abs(value))) > SIGNIFICANT_DIGITS:
                return self._text_cell(ref, str(value), row_style)
            return f'<c r="{ref}" s="{STYLE_INT}"><v>{value}</v></c>'
        if isinstance(value, Decimal):
            digits = len(value.as_tuple().digits)
            if digits > SIGNIFICANT_DIGITS:
                return self._text_cell(ref, format(value, "f"), row_style)
            return f'<c r="{ref}"><v>{format(value, "f")}</v></c>'
        return self._text_cell(ref, str(value), row_style)

    def close(self) -> None:
        self._write("</sheetData></worksheet>")


class XlsxWriter:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._archive = zipfile.ZipFile(self.path, "w", zipfile.ZIP_DEFLATED)
        self._sheets: list[str] = []

    def add_sheet(
        self,
        name: str,
        rows: Iterator[list[object]] | Iterable[list[object]],
        *,
        header: list[str] | None = None,
        widths: list[float] | None = None,
        title: str | None = None,
        preface: list[list[object]] | None = None,
    ) -> int:
        """Write one sheet and return the number of rows written. Names are limited to 31 chars."""
        if len(name) > 31 or any(c in name for c in "[]:*?/\\"):
            raise ValueError(f"nome de aba invalido: {name}")
        self._sheets.append(name)
        number = len(self._sheets)
        with self._archive.open(
            f"xl/worksheets/sheet{number}.xml", "w", force_zip64=True
        ) as stream:
            # Freeze up to the table header, which comes after the optional title and preface.
            frozen = (2 if title else 0) + (len(preface) + 1 if preface else 0)
            frozen += 1 if header else 0
            sheet = SheetWriter(stream, widths, frozen if header else 0)
            if title:
                sheet.write_row([title], style=STYLE_TITLE)
                sheet.write_row([])
            for line in preface or []:
                sheet.write_row(line, style=STYLE_WRAP)
            if preface:
                sheet.write_row([])
            if header:
                sheet.write_row(header, style=STYLE_HEADER)
            for row in rows:
                sheet.write_row(row)
            sheet.close()
        return sheet.rows

    def close(self) -> None:
        names = self._sheets
        content = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '<Default Extension="xml" ContentType="application/xml"/>',
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        ]
        for i in range(len(names)):
            content.append(
                f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            )
        content.append("</Types>")
        self._archive.writestr("[Content_Types].xml", "".join(content))
        self._archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        sheets = "".join(
            f'<sheet name="{escape(n, {chr(34): "&quot;"})}" sheetId="{i + 1}" r:id="rId{i + 1}"/>'
            for i, n in enumerate(names)
        )
        self._archive.writestr(
            "xl/workbook.xml",
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<workbook xmlns="{_NS}" xmlns:r="{_REL}"><sheets>{sheets}</sheets></workbook>',
        )
        rels = "".join(
            f'<Relationship Id="rId{i + 1}" Type="{_REL}/worksheet" '
            f'Target="worksheets/sheet{i + 1}.xml"/>'
            for i in range(len(names))
        )
        rels += f'<Relationship Id="rId{len(names) + 1}" Type="{_REL}/styles" Target="styles.xml"/>'
        self._archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>',
        )
        self._archive.writestr("xl/styles.xml", _STYLES)
        self._archive.close()

    def __enter__(self) -> XlsxWriter:
        return self

    def __exit__(self, *exc) -> None:
        if not self._archive.fp:  # already closed
            return
        if exc[0] is None:
            self.close()
        else:
            self._archive.close()


# -- reader ------------------------------------------------------------------------------------
def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _column_index(ref: str) -> int:
    value = 0
    for char in ref:
        if not char.isalpha():
            break
        value = value * 26 + (ord(char.upper()) - 64)
    return value - 1


def read_xlsx(path: Path) -> dict[str, list[list[str]]]:
    """Every sheet as rows of strings (blank cells as ''). For tests and reference reading."""
    result: dict[str, list[list[str]]] = {}
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in root:
                shared.append("".join(t.text or "" for t in si.iter() if _local(t.tag) == "t"))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        for sheet in (el for el in workbook.iter() if _local(el.tag) == "sheet"):
            rid = sheet.get(f"{{{_REL}}}id")
            target = targets[rid].lstrip("/")
            part = target if target.startswith("xl/") else f"xl/{target}"
            rows: list[list[str]] = []
            for _event, el in ET.iterparse(archive.open(part), events=("end",)):
                if _local(el.tag) != "row":
                    continue
                row: list[str] = []
                for cell in el:
                    if _local(cell.tag) != "c":
                        continue
                    idx = _column_index(cell.get("r", "A1"))
                    while len(row) <= idx:
                        row.append("")
                    kind = cell.get("t")
                    if kind == "inlineStr":
                        text = "".join(t.text or "" for t in cell.iter() if _local(t.tag) == "t")
                    else:
                        v = next((c for c in cell if _local(c.tag) == "v"), None)
                        text = (v.text or "") if v is not None else ""
                        if kind == "s" and text:
                            text = shared[int(text)]
                    row[idx] = text
                rows.append(row)
                el.clear()
            result[sheet.get("name", "")] = rows
    return result
