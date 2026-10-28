"""SYNTHETIC CGU NF-e monthly ZIPs. For tests only; none of this is official data.

Every name, municipality and identifier is invented and says so ("SINTETICO"). The access keys
are well formed (44 digits with a valid check digit) so the parsing rules can be exercised.
"""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

NOTE_HEADER = [
    "CHAVE DE ACESSO",
    "MODELO",
    "SÉRIE",
    "NÚMERO",
    "NATUREZA DA OPERAÇÃO",
    "DATA EMISSÃO",
    "EVENTO MAIS RECENTE",
    "DATA/HORA EVENTO MAIS RECENTE",
    "CPF/CNPJ Emitente",
    "RAZÃO SOCIAL EMITENTE",
    "UF EMITENTE",
    "MUNICÍPIO EMITENTE",
    "UF DESTINATÁRIO",
    "DESTINO DA OPERAÇÃO",
    "VALOR NOTA FISCAL",
]
ITEM_HEADER = [
    "CHAVE DE ACESSO",
    "MODELO",
    "SÉRIE",
    "NÚMERO",
    "NATUREZA DA OPERAÇÃO",
    "DATA EMISSÃO",
    "CPF/CNPJ Emitente",
    "RAZÃO SOCIAL EMITENTE",
    "UF EMITENTE",
    "MUNICÍPIO EMITENTE",
    "UF DESTINATÁRIO",
    "NÚMERO PRODUTO",
    "DESCRIÇÃO DO PRODUTO/SERVIÇO",
    "CÓDIGO NCM/SH",
    "NCM/SH (TIPO DE PRODUTO)",
    "CFOP",
    "QUANTIDADE",
    "UNIDADE",
    "VALOR UNITÁRIO",
    "VALOR TOTAL",
]
EVENT_HEADER = [
    "CHAVE DE ACESSO",
    "MODELO",
    "SÉRIE",
    "NÚMERO",
    "DATA EMISSÃO",
    "EVENTO",
    "DATA/HORA EVENTO",
    "DESCRIÇÃO EVENTO",
    "MOTIVO EVENTO",
]


def access_key(seed: int, month: str = "202401", uf_code: str = "35") -> str:
    """44 digits with a valid modulo 11 check digit, derived from ``seed``."""
    body = f"{uf_code}{month[2:]}{'99999999000199'}55{seed % 1000:03d}{seed:09d}1{seed % 10**8:08d}"
    body = body[:43]
    weights = [2, 3, 4, 5, 6, 7, 8, 9]
    total = sum(int(d) * weights[i % 8] for i, d in enumerate(reversed(body)))
    rest = total % 11
    dv = 0 if rest in (0, 1) else 11 - rest
    return f"{body}{dv}"


def note_row(
    seed: int,
    month: str = "202401",
    *,
    day: str | None = None,
    value: str = "100,00",
    uf: str = "SP",
    city: str = "MUNICÍPIO SINTÉTICO A",
    uf_dest: str = "RJ",
    event: str = "",
    key: str | None = None,
) -> list[str]:
    year, mm = month[:4], month[4:]
    return [
        key or access_key(seed, month),
        "55",
        "1",
        str(seed),
        "VENDA SINTETICA",
        f"{day or '10'}/{mm}/{year}",
        event,
        "",
        "00000000000000",
        "EMITENTE SINTETICO LTDA",
        uf,
        city,
        uf_dest,
        "1",
        value,
    ]


def item_row(
    key: str,
    number: str = "1",
    month: str = "202401",
    *,
    day: str | None = None,
    value: str = "100,00",
    quantity: str = "1,0000",
    unit: str = "UN",
    ncm: str = "01012100",
    cfop: str = "5102",
    uf: str = "SP",
    city: str = "MUNICÍPIO SINTÉTICO A",
    uf_dest: str = "RJ",
    tipo: str = "ANIMAIS SINTETICOS",
) -> list[str]:
    year, mm = month[:4], month[4:]
    return [
        key,
        "55",
        "1",
        "1",
        "VENDA SINTETICA",
        f"{day or '10'}/{mm}/{year}",
        "00000000000000",
        "EMITENTE SINTETICO LTDA",
        uf,
        city,
        uf_dest,
        number,
        "PRODUTO SINTETICO",
        ncm,
        tipo,
        cfop,
        quantity,
        unit,
        value,
        value,
    ]


def event_row(key: str, description: str, month: str = "202401") -> list[str]:
    return [key, "55", "1", "1", f"10/{month[4:]}/{month[:4]}", "110111", "", description, ""]


def _csv_bytes(header: list[str], rows: list[list[str]], *, encoding: str, delimiter: str) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=delimiter, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode(encoding)


def build_zip(
    path: Path,
    month: str,
    notes: list[list[str]],
    items: list[list[str]],
    events: list[list[str]] | None = None,
    *,
    encoding: str = "cp1252",
    delimiter: str = ";",
    note_header: list[str] | None = None,
    item_header: list[str] | None = None,
    extra_members: dict[str, bytes] | None = None,
) -> Path:
    """Write a monthly ZIP shaped like the official one, with synthetic content."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f"{month}_NFe_NotaFiscal.csv",
            _csv_bytes(note_header or NOTE_HEADER, notes, encoding=encoding, delimiter=delimiter),
        )
        archive.writestr(
            f"{month}_NFe_NotaFiscalItem.csv",
            _csv_bytes(item_header or ITEM_HEADER, items, encoding=encoding, delimiter=delimiter),
        )
        if events is not None:
            archive.writestr(
                f"{month}_NFe_NotaFiscalEvento.csv",
                _csv_bytes(EVENT_HEADER, events, encoding=encoding, delimiter=delimiter),
            )
        for name, data in (extra_members or {}).items():
            archive.writestr(name, data)
    return path


def baseline_month(path: Path, month: str = "202401") -> dict[str, int]:
    """Three notes, four items, one cancellation. Returns the figures the tests assert on."""
    k1, k2, k3 = (access_key(n, month) for n in (1, 2, 3))
    notes = [
        note_row(1, month, value="300,50", city="MUNICÍPIO SINTÉTICO A"),
        note_row(2, month, value="50,00", uf="MG", city="MUNICÍPIO SINTÉTICO B", uf_dest="MG"),
        note_row(
            3, month, value="1.234,56", event="Cancelamento de NF-e", city="MUNICÍPIO SINTÉTICO A"
        ),
    ]
    items = [
        item_row(k1, "1", month, value="100,50", quantity="2,5000"),
        item_row(k1, "2", month, value="200,00", quantity="1,0000", ncm="02011000", unit="KG"),
        item_row(k2, "1", month, value="50,00", uf="MG", city="MUNICÍPIO SINTÉTICO B"),
        item_row(k3, "1", month, value="1.234,56", quantity="3,0000"),
    ]
    events = [event_row(k3, "Cancelamento de NF-e homologado", month)]
    build_zip(path, month, notes, items, events)
    return {
        "notas": 3,
        "itens": 4,
        "valor_notas": 30050 + 5000 + 123456,
        "valor_itens": 10050 + 20000 + 5000 + 123456,
    }
