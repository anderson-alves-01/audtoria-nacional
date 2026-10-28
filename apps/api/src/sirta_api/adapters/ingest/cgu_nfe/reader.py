"""Streaming reader of the CSV tables inside a monthly ZIP. Nothing is extracted to disk."""

from __future__ import annotations

import csv
import io
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass

from sirta_api.domain.cgu_nfe import (
    KIND_EVENT,
    KIND_ITEM,
    KIND_NOTE,
    HeaderMap,
    SchemaError,
    detect_kind,
    map_header,
)

EXPECTED_DELIMITER = ";"
EXPECTED_ENCODING = "cp1252"
SAMPLE_BYTES = 256 * 1024
csv.field_size_limit(16 * 1024 * 1024)


@dataclass(frozen=True)
class TableFormat:
    member: str
    kind: str
    encoding: str
    delimiter: str
    bom: bool
    header: list[str]
    mapping: HeaderMap

    @property
    def matches_expected(self) -> bool:
        """The sample described semicolons and Windows-1252. UTF-8 is accepted but reported."""
        return self.delimiter == EXPECTED_DELIMITER and self.encoding in (
            EXPECTED_ENCODING,
            "utf-8",
        )


def detect_encoding(sample: bytes) -> tuple[str, bool]:
    """UTF-8 (with or without BOM) when the sample decodes strictly, otherwise Windows-1252."""
    bom = sample.startswith(b"\xef\xbb\xbf")
    try:
        # A cut at the end of the sample may split a multibyte character: ignore the last bytes.
        sample.decode("utf-8", errors="strict")
        return ("utf-8", bom)
    except UnicodeDecodeError as error:
        if error.start >= len(sample) - 4:
            return ("utf-8", bom)
    try:
        sample.decode("cp1252", errors="strict")
        return ("cp1252", False)
    except UnicodeDecodeError:
        return ("latin-1", False)


def detect_delimiter(header_line: str) -> str:
    counts = {d: header_line.count(d) for d in (";", ",", "\t", "|")}
    best = max(counts, key=lambda d: counts[d])
    return best if counts[best] > 0 else EXPECTED_DELIMITER


def _text_stream(raw: io.BufferedIOBase, encoding: str) -> io.TextIOWrapper:
    codec = "utf-8-sig" if encoding == "utf-8" else encoding
    return io.TextIOWrapper(raw, encoding=codec, errors="strict", newline="")


def inspect_member(archive: zipfile.ZipFile, name: str) -> TableFormat | None:
    """Format and header of one CSV member, or ``None`` when it is not one of the tables."""
    with archive.open(name) as raw:
        sample = raw.read(SAMPLE_BYTES)
    if not sample.strip():
        return None
    encoding, bom = detect_encoding(sample)
    codec = "utf-8-sig" if encoding == "utf-8" else encoding
    first_line = sample.decode(codec, errors="replace").split("\n", 1)[0].rstrip("\r")
    delimiter = detect_delimiter(first_line)
    header = next(csv.reader([first_line], delimiter=delimiter))
    kind = detect_kind(name, header)
    if kind is None:
        return None
    mapping = map_header(kind, header)
    return TableFormat(name, kind, encoding, delimiter, bom, header, mapping)


def find_tables(archive: zipfile.ZipFile) -> dict[str, list[TableFormat]]:
    """Every table of the ZIP, by kind. A kind may come in more than one member."""
    found: dict[str, list[TableFormat]] = {KIND_NOTE: [], KIND_ITEM: [], KIND_EVENT: []}
    for info in sorted(archive.infolist(), key=lambda i: i.filename):
        if info.is_dir() or not info.filename.lower().endswith(".csv"):
            continue
        table = inspect_member(archive, info.filename)
        if table is not None:
            found[table.kind].append(table)
    return found


def iter_rows(archive: zipfile.ZipFile, table: TableFormat) -> Iterator[tuple[int, list[str]]]:
    """(line number, fields) for every data row. The header is skipped.

    The line number counts physical records starting at 2 for the first data row, which is what a
    reviewer sees in a spreadsheet. A bad byte sequence stops the table with ``SchemaError``.
    """
    with archive.open(table.member) as raw:
        stream = _text_stream(raw, table.encoding)
        reader = csv.reader(stream, delimiter=table.delimiter, quotechar='"')
        try:
            next(reader)
            for number, row in enumerate(reader, start=2):
                if not row:
                    continue
                yield number, row
        except UnicodeDecodeError as error:
            raise SchemaError(f"{table.member}: codificação inesperada ({error.reason})") from error
        except csv.Error as error:
            raise SchemaError(f"{table.member}: CSV ilegível ({error})") from error
