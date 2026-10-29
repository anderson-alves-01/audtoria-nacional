"""Rules for the CGU electronic invoice (NF-e) monthly files. Pure functions, no I/O.

Source: Portal da Transparência, "Notas Fiscais" (CGU). One ZIP per month with three tables:
NotaFiscal (header), NotaFiscalItem (items) and NotaFiscalEvento (events).

Principles enforced here:
- Nothing is invented or estimated. A blank figure stays ``None``. It is never read as zero.
- Money is exact: integer cents. A figure that is not exactly representable in cents is refused
  (quarantined by the caller), never rounded.
- Identifiers (access key, CNPJ, NCM, CFOP) are text.
- The tax situation (cancelled or not) comes only from the events that the source provides.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

PROCESSING_VERSION = "cgu-nfe-v1"
SOURCE_ID = "CGU-NFE"
CATALOG_URL = "https://portaldatransparencia.gov.br/download-de-dados/notas-fiscais"
DICTIONARY_URL = "https://portaldatransparencia.gov.br/dicionario-de-dados/notas-fiscais"
DOWNLOAD_BASE = "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/nfe/"

FIRST_YEAR = 2021
LAST_YEAR = 2025

# --- Month states ---------------------------------------------------------------------------------
STATE_NOT_LISTED = "NAO_LISTADO"
STATE_PENDING = "DOWNLOAD_PENDENTE"
STATE_BLOCKED = "DOWNLOAD_BLOQUEADO"
STATE_INVALID = "ARQUIVO_INVALIDO"
STATE_VALIDATED = "BAIXADO_VALIDADO"
STATE_DONE = "PROCESSAMENTO_CONCLUIDO"
MONTH_STATES = (
    STATE_NOT_LISTED,
    STATE_PENDING,
    STATE_BLOCKED,
    STATE_INVALID,
    STATE_VALIDATED,
    STATE_DONE,
)

# --- Tax situation derived from the events --------------------------------------------------------
SIT_CANCELLED = "CANCELADA"
SIT_OTHER_EVENT = "EVENTO_NAO_CANCELAMENTO"
SIT_NO_EVENT = "SEM_EVENTO_INFORMADO"
# Item-only buckets: the item has no usable header in the same monthly file.
SIT_NO_NOTE = "ITEM_SEM_NOTA"
SIT_NOTE_QUARANTINED = "NOTA_EM_QUARENTENA"
SITUATIONS = (SIT_CANCELLED, SIT_OTHER_EVENT, SIT_NO_EVENT, SIT_NO_NOTE, SIT_NOTE_QUARANTINED)

KIND_NOTE = "NOTA"
KIND_ITEM = "ITEM"
KIND_EVENT = "EVENTO"

UFS = frozenset(
    "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split()
)


class CguNfeError(Exception):
    """Base error. Callers fail closed."""


class SchemaError(CguNfeError):
    """A required column is missing from a table."""


class ValueRefused(CguNfeError):
    """A value cannot be read without changing it."""


# --- Months ---------------------------------------------------------------------------------------
def requested_months() -> list[str]:
    """The 60 requested months, ``AAAAMM``, January 2021 to December 2025."""
    return [
        f"{year}{month:02d}" for year in range(FIRST_YEAR, LAST_YEAR + 1) for month in range(1, 13)
    ]


def is_month(value: str) -> bool:
    return bool(re.fullmatch(r"(19|20)\d{2}(0[1-9]|1[0-2])", value or ""))


def month_url(month: str) -> str:
    if not is_month(month):
        raise ValueError(f"Mês inválido: {month!r}")
    return f"{DOWNLOAD_BASE}{month}_NFe.zip"


def bronze_name(month: str) -> str:
    return f"{month}_NFe.zip"


def month_from_filename(name: str) -> str | None:
    match = re.search(r"(?<!\d)((?:19|20)\d{2}(?:0[1-9]|1[0-2]))(?!\d)", name)
    return match.group(1) if match else None


def derive_state(
    *,
    listed: bool,
    blocked: bool = False,
    invalid: bool = False,
    validated: bool = False,
    processed: bool = False,
) -> str:
    """The state is a function of recorded facts, never of a file name.

    Priority: a processed month stays processed. A validated file beats an old block, because a
    manually imported file settles the month. Invalid and blocked come before pending.
    """
    if processed:
        return STATE_DONE
    if validated:
        return STATE_VALIDATED
    if invalid:
        return STATE_INVALID
    if blocked:
        return STATE_BLOCKED
    if not listed:
        return STATE_NOT_LISTED
    return STATE_PENDING


# --- Text and headers -----------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", text) if not unicodedata.combining(char)
    )


def normalize_header(text: str) -> str:
    """Upper case, no accents, every non alphanumeric run becomes one space."""
    text = strip_accents((text or "").replace("\ufeff", "")).upper()
    return re.sub(r"[^A-Z0-9]+", " ", text).strip()


# canonical field -> accepted normalized header names (first is the dictionary name)
NOTE_FIELDS: dict[str, tuple[str, ...]] = {
    "chave": ("CHAVE DE ACESSO",),
    "modelo": ("MODELO",),
    "serie": ("SERIE",),
    "numero": ("NUMERO",),
    "natureza": ("NATUREZA DA OPERACAO",),
    "data_emissao": ("DATA EMISSAO",),
    "evento_recente": ("EVENTO MAIS RECENTE",),
    "data_evento": ("DATA HORA EVENTO MAIS RECENTE",),
    "doc_emitente": ("CPF CNPJ EMITENTE",),
    "uf_emitente": ("UF EMITENTE",),
    "municipio_emitente": ("MUNICIPIO EMITENTE",),
    "uf_destinatario": ("UF DESTINATARIO",),
    "destino_operacao": ("DESTINO DA OPERACAO",),
    "valor_nota": ("VALOR NOTA FISCAL",),
}
NOTE_REQUIRED = (
    "chave",
    "data_emissao",
    "evento_recente",
    "uf_emitente",
    "municipio_emitente",
    "uf_destinatario",
    "valor_nota",
)
ITEM_FIELDS: dict[str, tuple[str, ...]] = {
    "chave": ("CHAVE DE ACESSO",),
    "numero": ("NUMERO",),
    "data_emissao": ("DATA EMISSAO",),
    "doc_emitente": ("CPF CNPJ EMITENTE",),
    "uf_emitente": ("UF EMITENTE",),
    "municipio_emitente": ("MUNICIPIO EMITENTE",),
    "uf_destinatario": ("UF DESTINATARIO",),
    "numero_produto": ("NUMERO PRODUTO",),
    "descricao": ("DESCRICAO DO PRODUTO SERVICO",),
    "ncm": ("CODIGO NCM SH",),
    "ncm_tipo": ("NCM SH TIPO DE PRODUTO",),
    "cfop": ("CFOP", "CODIGO CFOP"),
    "quantidade": ("QUANTIDADE",),
    "unidade": ("UNIDADE", "UNIDADE DE MEDIDA"),
    "valor_unitario": ("VALOR UNITARIO",),
    "valor_total": ("VALOR TOTAL",),
}
ITEM_REQUIRED = (
    "chave",
    "numero_produto",
    "data_emissao",
    "uf_emitente",
    "municipio_emitente",
    "ncm",
    "cfop",
    "quantidade",
    "unidade",
    "valor_total",
)
EVENT_FIELDS: dict[str, tuple[str, ...]] = {
    "chave": ("CHAVE DE ACESSO",),
    "data_emissao": ("DATA EMISSAO",),
    "evento": ("DESCRICAO EVENTO", "EVENTO"),
    "data_evento": ("DATA HORA EVENTO", "DATA HORA EVENTO MAIS RECENTE"),
    "motivo": ("MOTIVO EVENTO",),
}
EVENT_REQUIRED = ("chave", "evento")

SCHEMAS = {
    KIND_NOTE: (NOTE_FIELDS, NOTE_REQUIRED),
    KIND_ITEM: (ITEM_FIELDS, ITEM_REQUIRED),
    KIND_EVENT: (EVENT_FIELDS, EVENT_REQUIRED),
}


@dataclass(frozen=True)
class HeaderMap:
    kind: str
    index: dict[str, int]  # canonical field -> column position
    unknown: tuple[str, ...]  # headers that the layout does not know (reported, never dropped)
    width: int


def map_header(kind: str, header: list[str]) -> HeaderMap:
    """Map a header row to canonical fields. A missing required field fails closed."""
    fields, required = SCHEMAS[kind]
    by_name: dict[str, int] = {}
    for position, name in enumerate(header):
        by_name.setdefault(normalize_header(name), position)
    index: dict[str, int] = {}
    used: set[int] = set()
    for canonical, accepted in fields.items():
        for candidate in accepted:
            if candidate in by_name and by_name[candidate] not in used:
                index[canonical] = by_name[candidate]
                used.add(by_name[candidate])
                break
    missing = [name for name in required if name not in index]
    if missing:
        raise SchemaError(f"Tabela {kind}: colunas obrigatórias ausentes: {', '.join(missing)}")
    unknown = tuple(header[i] for i in range(len(header)) if i not in used)
    return HeaderMap(kind=kind, index=index, unknown=unknown, width=len(header))


def detect_kind(member_name: str, header: list[str]) -> str | None:
    """Table kind from the member name, confirmed or replaced by the header."""
    name = normalize_header(member_name.rsplit("/", 1)[-1].rsplit(".", 1)[0])
    normalized = {normalize_header(h) for h in header}
    if "NOTAFISCALITEM" in name.replace(" ", "") or "CODIGO NCM SH" in normalized:
        return KIND_ITEM
    if "NOTAFISCALEVENTO" in name.replace(" ", "") or "MOTIVO EVENTO" in normalized:
        return KIND_EVENT
    if "NOTAFISCAL" in name.replace(" ", "") or "VALOR NOTA FISCAL" in normalized:
        return KIND_NOTE
    return None


# --- Numbers --------------------------------------------------------------------------------------
def parse_decimal(text: str | None) -> Decimal | None:
    """Exact decimal. Blank is ``None``. Comma is the decimal mark of the source.

    ``1.234,56`` reads as 1234.56 (dot as thousands mark only when a comma is present). A lone
    dot is read as a decimal point. Anything else raises ``ValueRefused``.
    """
    if text is None:
        return None
    value = text.strip().replace("\xa0", "").replace(" ", "")
    if value == "":
        return None
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    elif value.count(".") > 1:
        raise ValueRefused(f"Número ambíguo: {text!r}")
    if not re.fullmatch(r"[+-]?\d+(\.\d+)?", value):
        raise ValueRefused(f"Número inválido: {text!r}")
    try:
        return Decimal(value)
    except InvalidOperation as error:  # pragma: no cover - the regex already guards it
        raise ValueRefused(f"Número inválido: {text!r}") from error


def to_cents(value: Decimal | None) -> int | None:
    """Integer cents, only when the figure is exact to the cent. Never rounds."""
    if value is None:
        return None
    scaled = value * 100
    if scaled != scaled.to_integral_value():
        raise ValueRefused(f"Valor com mais de duas casas decimais: {value}")
    return int(scaled)


def cents_to_text(cents: int | None) -> str:
    """``12345`` -> ``123,45``. Blank for ``None`` (never a zero)."""
    if cents is None:
        return ""
    sign = "-" if cents < 0 else ""
    whole, frac = divmod(abs(cents), 100)
    return f"{sign}{whole},{frac:02d}"


def decimal_to_text(value: Decimal | None) -> str:
    """Decimal with comma, no exponent and no trailing change of precision."""
    if value is None:
        return ""
    return format(value, "f").replace(".", ",")


# --- Dates ----------------------------------------------------------------------------------------
_DATE_FORMATS = (
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
)


def parse_date(text: str | None) -> date | None:
    value = (text or "").strip()
    if not value:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value[:19], fmt).date()
        except ValueError:
            continue
    raise ValueRefused(f"Data inválida: {text!r}")


def month_of(day: date) -> str:
    return f"{day.year}{day.month:02d}"


# --- Identifiers ----------------------------------------------------------------------------------
def clean_identifier(text: str | None) -> str:
    """Identifier as text. Only surrounding blanks are removed."""
    return (text or "").strip()


def is_access_key(value: str) -> bool:
    return bool(re.fullmatch(r"\d{44}", value or ""))


def access_key_dv_ok(key: str) -> bool:
    """Check digit of the 44 digit access key (modulo 11). Reported, not used to reject."""
    if not is_access_key(key):
        return False
    weights = [2, 3, 4, 5, 6, 7, 8, 9]
    total = sum(int(d) * weights[i % 8] for i, d in enumerate(reversed(key[:43])))
    remainder = total % 11
    expected = 0 if remainder in (0, 1) else 11 - remainder
    return expected == int(key[43])


def key_digest(key: str) -> bytes:
    return hashlib.blake2b(key.encode("utf-8"), digest_size=16).digest()


def item_digest(key: str, item_number: str) -> bytes:
    return hashlib.blake2b(f"{key}|{item_number}".encode(), digest_size=16).digest()


def fingerprint(values: list[str]) -> bytes:
    """Fingerprint of the original row content (to tell identical from conflicting copies)."""
    joined = "\x1f".join(values).encode("utf-8", "replace")
    return hashlib.blake2b(joined, digest_size=8).digest()


# --- Situation ------------------------------------------------------------------------------------
def classify_situation(latest_event: str | None, events: set[str] | frozenset[str]) -> str:
    """Tax situation from the events the source provides.

    Cancelled: the latest event or any event of the events table contains CANCEL. A cancellation
    is terminal, so an earlier cancellation counts even if a later event is recorded. This rule is
    the one of the previous extraction, kept to preserve the reference scope.

    Not cancelled by the events: the note has events and none is a cancellation. This does not
    prove the note is valid for tax purposes. No event at all is reported as such, never as
    authorized.
    """
    texts = [normalize_header(latest_event or "")] + [normalize_header(e) for e in events]
    texts = [t for t in texts if t]
    if any("CANCEL" in t for t in texts):
        return SIT_CANCELLED
    if texts:
        return SIT_OTHER_EVENT
    return SIT_NO_EVENT


# --- Simulator series (UF emitente × year) --------------------------------------------------------
YEARS = tuple(range(FIRST_YEAR, LAST_YEAR + 1))
VALUE_KIND_OBSERVED = "OBSERVED_DOCUMENT_CENTS"
SIMULATOR_BANNER = (
    "NF-e da CGU (Portal da Transparência), UF do emitente. Quantidade = número de itens. "
    "Valor = soma dos itens em centavos, visão exceto canceladas. Não é o mercado, todas as "
    "compras públicas nem NFS-e. Valor de documento não é pagamento. Cobertura PARCIAL enquanto "
    "houver mês pedido sem ZIP. Imposto do Simulador = valor × alíquota (alíquotas não homologadas)."
)
SIMULATOR_FORMULA = (
    "itens_exceto_canceladas = itens_bruto − itens_cancelados; "
    "valor_itens_exceto_canceladas = valor_itens_bruto − valor_itens_cancelados. "
    "Cancelada quando o evento contém CANCEL. UF é a do emitente."
)


def cents_to_decimal_text(cents: int) -> str:
    """API money: ``12345`` → ``123.45``. Exact cents, period decimal, two places."""
    return format(Decimal(cents).scaleb(-2), "f")


def coverage_of(requested: list[str], processed: list[str]) -> tuple[str, list[str]]:
    """PARCIAL while any requested month is missing. AUSENTE when nothing was processed."""
    done = set(processed)
    missing = [month for month in requested if month not in done]
    if not processed:
        return "AUSENTE", missing
    if missing:
        return "PARCIAL", missing
    return "COMPLETO", []


@dataclass(frozen=True, slots=True)
class YearUfMeasures:
    """Observed item and note totals by issuer UF and year. Simulator uses except-cancelled items."""

    year: int
    uf: str
    itens_bruto: int
    valor_itens_bruto_cents: int
    itens_cancelados: int
    valor_itens_cancelados_cents: int
    notas_bruto: int
    valor_notas_bruto_cents: int
    notas_canceladas: int
    valor_notas_canceladas_cents: int

    @property
    def itens(self) -> int:
        return self.itens_bruto - self.itens_cancelados

    @property
    def valor_itens_cents(self) -> int:
        return self.valor_itens_bruto_cents - self.valor_itens_cancelados_cents

    @property
    def notas(self) -> int:
        return self.notas_bruto - self.notas_canceladas

    @property
    def valor_notas_cents(self) -> int:
        return self.valor_notas_bruto_cents - self.valor_notas_canceladas_cents


def _add_bucket(
    buckets: dict[tuple[int, str], dict[str, int]],
    year: str,
    uf: str,
    situation: str,
    count: int,
    cents: int,
    kind: str,
) -> None:
    key = (int(year), uf)
    slot = buckets.setdefault(
        key,
        {
            "itens_bruto": 0,
            "valor_itens_bruto_cents": 0,
            "itens_cancelados": 0,
            "valor_itens_cancelados_cents": 0,
            "notas_bruto": 0,
            "valor_notas_bruto_cents": 0,
            "notas_canceladas": 0,
            "valor_notas_canceladas_cents": 0,
        },
    )
    cancelled = situation == SIT_CANCELLED
    if kind == "item":
        slot["itens_bruto"] += count
        slot["valor_itens_bruto_cents"] += cents
        if cancelled:
            slot["itens_cancelados"] += count
            slot["valor_itens_cancelados_cents"] += cents
    else:
        slot["notas_bruto"] += count
        slot["valor_notas_bruto_cents"] += cents
        if cancelled:
            slot["notas_canceladas"] += count
            slot["valor_notas_canceladas_cents"] += cents


def roll_year_uf(
    *,
    item_rows: Iterable[tuple[str, str, str, int, int]],
    note_rows: Iterable[tuple[str, str, str, int, int]],
) -> list[YearUfMeasures]:
    """Roll (year, uf, situacao, count, cents) rows. Blank stays out: empty input yields []."""
    buckets: dict[tuple[int, str], dict[str, int]] = {}
    for year, uf, situation, count, cents in item_rows:
        _add_bucket(buckets, year, uf, situation, count, cents, "item")
    for year, uf, situation, count, cents in note_rows:
        _add_bucket(buckets, year, uf, situation, count, cents, "note")
    return [
        YearUfMeasures(year=year, uf=uf, **values)
        for (year, uf), values in sorted(buckets.items())
    ]


def series_item(row: YearUfMeasures) -> dict:
    """JSON item for GET /v1/cgu-nfe. Except-cancelled is the public measure."""
    return {
        "ano": row.year,
        "uf": row.uf,
        "itens": row.itens,
        "valorItens": cents_to_decimal_text(row.valor_itens_cents),
        "notas": row.notas,
        "valorNotas": cents_to_decimal_text(row.valor_notas_cents),
        "itensBruto": row.itens_bruto,
        "valorItensBruto": cents_to_decimal_text(row.valor_itens_bruto_cents),
        "itensCancelados": row.itens_cancelados,
        "valorItensCancelados": cents_to_decimal_text(row.valor_itens_cancelados_cents),
    }
