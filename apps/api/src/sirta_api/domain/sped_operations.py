"""SPED NF-e operations by UF and CFOP: shapes, classification and reconciliation.

The R$ figures in this source are an ESTIMATED ALLOCATION of national totals, never a fiscal
value of the UF. Nothing here sums across operations and nothing creates a tax credit.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from decimal import Decimal

SPED_SOURCE_ID = "SPED-NFE-UF-CFOP"
SPED_LAYOUT_VERSION = "sped-nfe-uf-cfop-v1"
SPED_COMPETENCE = "2021-25"
SPED_VALUE_KIND = "ESTIMATED_ALLOCATION"
SPED_BANNER = (
    "Base exploratória, não homologada. O valor por UF é rateio estimado de totais nacionais, "
    "não valor fiscal efetivo. Não é crédito tributário."
)

YEARS = (2021, 2022, 2023, 2024, 2025)
UFS = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
)  # fmt: skip
OPERATIONS = (
    "Compras",
    "Vendas",
    "Transferências",
    "Doações / bonificações / brindes",
    "Serviços Prestados",
    "Serviços Tomados",
    "Outras Saídas",
)
INBOUND_OPERATIONS = frozenset({"Compras", "Serviços Tomados"})
EXPECTED_SERIES_ROWS = len(UFS) * len(YEARS) * len(OPERATIONS)
MAX_ERRORS = 50


@dataclass(frozen=True)
class SpedSerieRow:
    year: int
    uf: str
    operation: str
    quantity: int
    estimated_value: Decimal | None
    comparable_quantity: int | None = None
    comparable_share: Decimal | None = None
    cfop_pairs: int | None = None
    covered_quantity: int | None = None


@dataclass(frozen=True)
class SpedBaseRow:
    uf: str
    cfop: str
    operation: str
    year: int
    quantity: int
    estimated_value: Decimal | None


@dataclass
class SpedWorkbook:
    serie: list[SpedSerieRow]
    base: list[SpedBaseRow]
    consolidated: dict[tuple[str, str, str], Decimal | None]


@dataclass
class ReconciliationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    series_rows: int = 0
    base_rows: int = 0
    base_facts: int = 0
    consolidated_cells: int = 0
    max_value_difference: Decimal = Decimal("0")
    classification_mismatches: int = 0
    transfer_quantity: int = 0
    transfer_unconfirmed_quantity: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def fail(self, message: str) -> None:
        if len(self.errors) < MAX_ERRORS:
            self.errors.append(message)
        elif len(self.errors) == MAX_ERRORS:
            self.errors.append("Há mais divergências além destas.")


def classify_cfop(cfop: str) -> str | None:
    """Operational group by CFOP prefix, following the rules published with the file.

    Aggregator codes ending in 00 or 50 and inbound codes outside the listed groups are
    excluded and return None. The rules are approximate by design (the source says so).
    """
    if not re.fullmatch(r"[123567]\d{3}", cfop) or cfop.endswith(("00", "50")):
        return None
    rest = int(cfop[1:])
    if cfop[0] in "123":
        if 100 <= rest <= 199 or rest in (401, 403, 406, 407):
            return "Compras"
        if 300 <= rest <= 399:
            return "Serviços Tomados"
        return None
    if rest == 910:
        return "Doações / bonificações / brindes"
    if 151 <= rest <= 199:
        return "Transferências"
    if 100 <= rest <= 199 or rest in (401, 402, 403, 404, 405, 408, 409):
        return "Vendas"
    if 300 <= rest <= 399:
        return "Serviços Prestados"
    return "Outras Saídas"


# --- Transfer methodology (SIRTA) -------------------------------------------------------
# Source: official CFOP table (Sefaz-PE, cfop.htm), read 2026-10-28. Only the codes listed
# there as transfers between establishments of the same company are CONFIRMED. Codes in the
# same range that the table does not define (1.155-1.159, 1.190, 2.155-2.159, 2.170, 5.154,
# 5.157-5.199, 6.157-6.199, 7.15x) stay PENDING: nothing is inferred from the 15x prefix.
DIRECTION_RECEIVED = "RECEBIDA"
DIRECTION_SENT = "REMETIDA"
TRANSFER_DIRECTIONS = (DIRECTION_RECEIVED, DIRECTION_SENT)
CLASS_CONFIRMED = "CONFIRMADA"
CLASS_PENDING = "PENDENTE_CLASSIFICACAO"
CLASS_EXCLUDED = "EXCLUIDA"
TRANSFER_OPERATION = "Transferências"
CFOP_TABLE_SOURCE = "Tabela oficial de CFOP (Sefaz-PE, cfop.htm), lida em 2026-10-28"
TRANSFER_RECEIVED_CFOPS = frozenset(
    {"1151", "1152", "1153", "1154", "2151", "2152", "2153", "2154"}
)
TRANSFER_SENT_CFOPS = frozenset(
    {"5151", "5152", "5153", "5155", "5156", "6151", "6152", "6153", "6155", "6156"}
)
# Pending classification codes the user named explicitly, kept for documentation and tests.
PENDING_NAMED_CFOPS = frozenset({"1159", "2159", "1190", "2170"})


@dataclass(frozen=True)
class CfopClassification:
    """SIRTA classification of a CFOP: operation, direction and how sure we are."""

    operation: str | None
    direction: str | None
    status: str
    reason: str


def classify_cfop_sirta(cfop: str) -> CfopClassification:
    """Classification by the SIRTA methodology (never by prefix alone for transfers).

    - Confirmed transfers get an operation "Transferências" and a direction.
    - Codes in the transfer ranges that the official table does not define are PENDING and
      have no operation: they are not Compras and not Transferências until a source says so.
    - Everything else follows the rule published with the workbook (`classify_cfop`).
    """
    if not re.fullmatch(r"[123567]\d{3}", cfop) or cfop.endswith(("00", "50")):
        return CfopClassification(None, None, CLASS_EXCLUDED, "Código agregador ou inválido.")
    if cfop in TRANSFER_RECEIVED_CFOPS:
        return CfopClassification(
            TRANSFER_OPERATION, DIRECTION_RECEIVED, CLASS_CONFIRMED, CFOP_TABLE_SOURCE
        )
    if cfop in TRANSFER_SENT_CFOPS:
        return CfopClassification(
            TRANSFER_OPERATION, DIRECTION_SENT, CLASS_CONFIRMED, CFOP_TABLE_SOURCE
        )
    rest = int(cfop[1:])
    inbound_pending = cfop[0] in "12" and (151 <= rest <= 159 or cfop in PENDING_NAMED_CFOPS)
    outbound_pending = cfop[0] in "567" and 151 <= rest <= 199
    if inbound_pending or outbound_pending:
        return CfopClassification(
            None,
            None,
            CLASS_PENDING,
            "Código fora da lista de transferências da tabela oficial de CFOP; "
            "significado não confirmado.",
        )
    published = classify_cfop(cfop)
    if published is None:
        return CfopClassification(None, None, CLASS_EXCLUDED, "Exclusão publicada na planilha.")
    return CfopClassification(published, None, CLASS_CONFIRMED, "Regra publicada na planilha.")


def assert_single_direction(directions: Iterable[str | None]) -> str | None:
    """Return the only transfer direction present, or refuse to mix both.

    Received and sent transfers can be the same movement seen from two establishments, so
    adding them double counts. A distinct count needs document identity or a proven rule.
    """
    seen = {direction for direction in directions if direction is not None}
    if len(seen) > 1:
        raise ValueError(
            "Transferências recebidas e remetidas não podem ser somadas: risco de dupla "
            "contagem. Use uma direção por vez."
        )
    return next(iter(seen), None)


def _tolerance(parts: int, total: Decimal) -> Decimal:
    # Each published cell is rounded to cents, so a sum of n cells may drift by n * 0.005.
    return Decimal("0.01") * (parts + 1) + abs(total) * Decimal("0.000001")


def reconcile(workbook: SpedWorkbook) -> ReconciliationReport:
    report = ReconciliationReport()
    report.series_rows = len(workbook.serie)
    report.base_facts = len(workbook.base)
    report.base_rows = len({(row.uf, row.cfop) for row in workbook.base})
    report.consolidated_cells = len(workbook.consolidated)

    seen: set[tuple[int, str, str]] = set()
    series_by_key: dict[tuple[str, int, str], SpedSerieRow] = {}
    for row in workbook.serie:
        key = (row.year, row.uf, row.operation)
        if row.uf not in UFS:
            report.fail(f"Série anual: UF inválida {row.uf!r}.")
        if row.year not in YEARS:
            report.fail(f"Série anual: ano fora de 2021 a 2025 ({row.year}).")
        if row.operation not in OPERATIONS:
            report.fail(f"Série anual: operação desconhecida {row.operation!r}.")
        if row.quantity < 0:
            report.fail(f"Série anual: quantidade negativa em {key}.")
        if row.estimated_value is not None and row.estimated_value < 0:
            report.fail(f"Série anual: valor negativo em {key}.")
        if key in seen:
            report.fail(f"Série anual: linha duplicada {key}.")
        seen.add(key)
        series_by_key[(row.uf, row.year, row.operation)] = row
    if len(workbook.serie) != EXPECTED_SERIES_ROWS:
        report.fail(
            f"Série anual: esperadas {EXPECTED_SERIES_ROWS} linhas "
            f"(27 UFs x 5 anos x 7 operações), recebidas {len(workbook.serie)}."
        )

    cfop_operation: dict[str, str] = {}
    base_sum: dict[tuple[str, int, str], tuple[int, Decimal | None, int]] = {}
    base_seen: set[tuple[str, str, int]] = set()
    for row in workbook.base:
        if row.uf not in UFS:
            report.fail(f"Base CFOP: UF inválida {row.uf!r}.")
        if not re.fullmatch(r"\d{4}", row.cfop):
            report.fail(f"Base CFOP: CFOP inválido {row.cfop!r}.")
        if row.operation not in OPERATIONS:
            report.fail(f"Base CFOP: operação desconhecida {row.operation!r} no CFOP {row.cfop}.")
        if row.quantity < 0 or (row.estimated_value is not None and row.estimated_value < 0):
            report.fail(f"Base CFOP: valor negativo em {row.uf} {row.cfop} {row.year}.")
        inbound = row.operation in INBOUND_OPERATIONS
        if row.cfop[:1] and (row.cfop[0] in "123") != inbound:
            report.fail(
                f"Base CFOP: CFOP {row.cfop} não combina com a operação {row.operation!r} "
                "(entrada x saída)."
            )
        previous = cfop_operation.setdefault(row.cfop, row.operation)
        if previous != row.operation:
            report.fail(f"Base CFOP: CFOP {row.cfop} aparece em duas operações.")
        line = (row.uf, row.cfop, row.year)
        if line in base_seen:
            report.fail(f"Base CFOP: linha duplicada {line}.")
        base_seen.add(line)
        key = (row.uf, row.year, row.operation)
        qty, value, parts = base_sum.get(key, (0, None, 0))
        if row.estimated_value is not None:
            value = (value or Decimal("0")) + row.estimated_value
        base_sum[key] = (qty + row.quantity, value, parts + 1)

    for key, row in series_by_key.items():
        qty, value, parts = base_sum.get(key, (0, None, 0))
        label = f"{key[0]} {key[1]} {key[2]}"
        if qty != row.quantity:
            report.fail(
                f"Base CFOP não bate com a Série anual em quantidade ({label}): "
                f"{qty} contra {row.quantity}."
            )
        if (value is None) != (row.estimated_value is None) and not (
            (value in (None, Decimal("0"))) and (row.estimated_value in (None, Decimal("0")))
        ):
            report.fail(
                f"Base CFOP não bate com a Série anual: valor ausente em um lado ({label})."
            )
        elif value is not None and row.estimated_value is not None:
            difference = abs(value - row.estimated_value)
            report.max_value_difference = max(report.max_value_difference, difference)
            if difference > _tolerance(parts, row.estimated_value):
                report.fail(
                    f"Base CFOP não bate com a Série anual em valor ({label}): "
                    f"diferença {difference}."
                )
    for key in base_sum:
        if key not in series_by_key:
            report.fail(f"Base CFOP tem combinação sem Série anual: {key}.")

    totals: dict[tuple[str, str], tuple[int, Decimal | None, int]] = {}
    for row in workbook.serie:
        qty, value, parts = totals.get((row.uf, row.operation), (0, None, 0))
        if row.estimated_value is not None:
            value = (value or Decimal("0")) + row.estimated_value
        totals[(row.uf, row.operation)] = (qty + row.quantity, value, parts + 1)
    for (uf, operation), (qty, value, parts) in totals.items():
        published_qty = workbook.consolidated.get((uf, operation, "qty"))
        published_value = workbook.consolidated.get((uf, operation, "value"))
        if published_qty is None or int(published_qty) != qty:
            report.fail(
                f"Consolidado UF não bate com a Série anual em quantidade ({uf} {operation})."
            )
        if value is None:
            if published_value not in (None, Decimal("0")):
                report.fail(f"Consolidado UF tem valor sem base na Série anual ({uf} {operation}).")
        elif published_value is None or abs(published_value - value) > _tolerance(parts, value):
            report.fail(f"Consolidado UF não bate com a Série anual em valor ({uf} {operation}).")

    for row in workbook.base:
        expected = classify_cfop(row.cfop)
        if expected is not None and expected != row.operation:
            report.classification_mismatches += 1
        if row.operation == TRANSFER_OPERATION:
            report.transfer_quantity += row.quantity
            if classify_cfop_sirta(row.cfop).status != CLASS_CONFIRMED:
                report.transfer_unconfirmed_quantity += row.quantity
    if report.transfer_unconfirmed_quantity:
        share = 100 * report.transfer_unconfirmed_quantity / max(report.transfer_quantity, 1)
        report.warnings.append(
            f"{share:.1f}% da quantidade de Transferências está em CFOPs que a tabela oficial "
            "não lista como transferência (classificação pendente)."
        )
    if report.classification_mismatches:
        report.warnings.append(
            f"{report.classification_mismatches} linhas da Base CFOP divergem da regra de prefixos "
            "publicada (a classificação da fonte é aproximada)."
        )
    return report
