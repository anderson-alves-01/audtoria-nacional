"""Comparison with the earlier partial extraction (``docs/data``).

The earlier package is a reference, not a target. A month is only called reproduced when the same
SHA-256 ZIP was processed and the counts match. When the source files are absent or different the
report says so and nothing is claimed.
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sirta_api.adapters.ingest.cgu_nfe.inventory import month_statuses
from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.adapters.ingest.cgu_nfe.xlsx import read_xlsx
from sirta_api.domain.cgu_nfe import (
    PROCESSING_VERSION,
    SIT_CANCELLED,
    STATE_DONE,
    CguNfeError,
    parse_decimal,
    requested_months,
    to_cents,
)

MANIFEST_MEMBER = "Manifesto_auditoria.csv"
DETAIL_MEMBER = "CGU_2021_2025_NCM_CFOP_UF_Unidade.csv"


class ReferenceError_(CguNfeError):  # noqa: N818
    pass


@dataclass
class ReferenceMonth:
    month: str
    notes: int
    items: int
    sha256: str
    url: str
    # from the earlier workbook (cents), when it is available
    notes_cents: int | None = None
    items_cents: int | None = None
    cancelled_cents: int | None = None


@dataclass
class Reference:
    months: dict[str, ReferenceMonth]
    detail_rows: int
    detail_items: int
    detail_value_cents: int
    detail_by_year: dict[str, tuple[int, int]]  # year -> (items, cents)

    @property
    def hashes(self) -> dict[str, str]:
        return {m: r.sha256 for m, r in self.months.items()}

    @property
    def notes_total(self) -> int:
        return sum(r.notes for r in self.months.values())

    @property
    def items_total(self) -> int:
        return sum(r.items for r in self.months.values())


SERIES_SHEET = "Série histórica"


def _cents(text: str) -> int | None:
    """Cents from a workbook cell. The earlier workbook stored floats: accept only exact cents."""
    if text == "":
        return None
    try:
        value = Decimal(text)
    except InvalidOperation:
        return None
    cents = (value * 100).quantize(Decimal(1))
    return int(cents) if abs(value * 100 - cents) < Decimal("0.01") else None


def _load_series(xlsx_path: Path, months: dict[str, ReferenceMonth]) -> None:
    sheets = read_xlsx(xlsx_path)
    rows = sheets.get(SERIES_SHEET, [])
    start = next((i for i, r in enumerate(rows) if r[:1] == ["Mês do arquivo"]), None)
    if start is None:
        return
    for row in rows[start + 1 :]:
        month = row[0] if row else ""
        if month in months and len(row) >= 6:
            ref = months[month]
            ref.notes_cents = _cents(row[2])
            ref.items_cents = _cents(row[4])
            ref.cancelled_cents = _cents(row[5])


def load_reference(
    zip_path: Path, *, detail: bool = True, xlsx_path: Path | None = None
) -> Reference:
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        raise ReferenceError_(f"pacote de referência ausente: {zip_path}")
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        if MANIFEST_MEMBER not in names:
            raise ReferenceError_(f"{MANIFEST_MEMBER} ausente em {zip_path.name}")
        text = archive.read(MANIFEST_MEMBER).decode("utf-8-sig")
        months: dict[str, ReferenceMonth] = {}
        for row in csv.DictReader(io.StringIO(text), delimiter=";"):
            if not row["SHA-256 do ZIP"]:
                continue  # month the earlier extraction did not receive
            months[row["Mês"]] = ReferenceMonth(
                row["Mês"],
                int(row["Notas lidas"]),
                int(row["Itens lidos"]),
                row["SHA-256 do ZIP"],
                row["URL oficial"],
            )
        rows = items = cents = 0
        by_year: dict[str, tuple[int, int]] = {}
        if detail and DETAIL_MEMBER in names:
            with archive.open(DETAIL_MEMBER) as raw:
                reader = csv.DictReader(
                    io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""), delimiter=";"
                )
                for row in reader:
                    rows += 1
                    n = int(row["Itens"])
                    c = to_cents(parse_decimal(row["Valor itens R$"])) or 0
                    items += n
                    cents += c
                    year_items, year_cents = by_year.get(row["Ano"], (0, 0))
                    by_year[row["Ano"]] = (year_items + n, year_cents + c)
    if xlsx_path is not None and Path(xlsx_path).is_file():
        _load_series(Path(xlsx_path), months)
    return Reference(months, rows, items, cents, by_year)


@dataclass
class ReconcileRow:
    month: str
    state: str
    reference: str  # notes / items of the earlier extraction
    local: str
    hash_match: str
    verdict: str
    values: str = "-"  # comparison of the monetary totals of the month


@dataclass
class ReconcileReport:
    rows: list[ReconcileRow] = field(default_factory=list)
    summary: list[str] = field(default_factory=list)
    reproduced: bool = False


def _fmt_money(cents: int) -> str:
    whole, frac = divmod(cents, 100)
    return f"R$ {whole:,}.{frac:02d}"


def _local_values(store: Store, month: str) -> tuple[int, int, int]:
    conn = store.conn
    notes = conn.execute(
        "SELECT COALESCE(SUM(valor_cents),0) FROM agg_nota_mun WHERE month=?", (month,)
    ).fetchone()[0]
    items = conn.execute(
        "SELECT COALESCE(SUM(valor_cents),0) FROM agg_item WHERE month=?", (month,)
    ).fetchone()[0]
    cancelled = conn.execute(
        "SELECT COALESCE(SUM(valor_cents),0) FROM agg_nota_mun WHERE month=? AND situacao=?",
        (month, SIT_CANCELLED),
    ).fetchone()[0]
    return int(notes), int(items), int(cancelled)


def _compare_values(store: Store, month: str, ref: ReferenceMonth) -> str:
    if ref.notes_cents is None and ref.items_cents is None:
        return "SEM_VALORES_NA_REFERENCIA"
    notes, items, cancelled = _local_values(store, month)
    pairs = (
        ("valor das notas", ref.notes_cents, notes),
        ("valor dos itens", ref.items_cents, items),
        ("valor de notas canceladas", ref.cancelled_cents, cancelled),
    )
    diffs = [
        f"{name}: ref={_fmt_money(r)} local={_fmt_money(v)}"
        for name, r, v in pairs
        if r is not None and r != v
    ]
    return "IGUAIS" if not diffs else "DIVERGENTES (" + "; ".join(diffs) + ")"


def reconcile_reference(store: Store, reference: Reference) -> ReconcileReport:
    report = ReconcileReport()
    statuses = {s.month: s for s in month_statuses(store)}
    reproduced = comparable = 0
    reproduced_months: set[str] = set()
    for month in requested_months():
        status = statuses[month]
        ref = reference.months.get(month)
        ref_text = f"{ref.notes} notas / {ref.items} itens" if ref else "sem registro"
        file = store.current_file(month)
        processing = store.latest_processing(month) if status.state == STATE_DONE else None
        local_text = "sem dados locais"
        hash_match = "-"
        values = "-"
        counts: dict = {}
        if processing is not None:
            counts = json.loads(processing["counts"] or "{}")
            read_n, read_i = counts.get("notas_lidas", 0), counts.get("itens_lidos", 0)
            local_text = (
                f"{counts.get('notas_aceitas', 0)} notas / {counts.get('itens_aceitos', 0)} "
                f"itens (lidas: {read_n} / {read_i})"
            )
        if ref is None:
            verdict = "SEM_REFERENCIA"
        elif file is None:
            verdict = "SEM_ZIP_LOCAL"
        else:
            hash_match = "SIM" if file["sha256"] == ref.sha256 else "NAO"
            if processing is None:
                verdict = "ZIP_LOCAL_NAO_PROCESSADO"
            else:
                comparable += 1
                same_counts = read_n == ref.notes and read_i == ref.items
                if hash_match == "SIM" and same_counts:
                    values = _compare_values(store, month, ref)
                    if values.startswith("DIVERGENTES"):
                        verdict = "VALORES_DIVERGENTES"
                    else:  # equal values, or a reference with no values (hash and counts decide)
                        verdict = "REPRODUZIDO"
                        reproduced += 1
                        reproduced_months.add(month)
                elif hash_match == "NAO":
                    verdict = "ARQUIVO_DIFERENTE_NAO_COMPARAVEL"
                else:
                    verdict = "CONTAGEM_DIVERGENTE"
        report.rows.append(
            ReconcileRow(month, status.state, ref_text, local_text, hash_match, verdict, values)
        )

    report.summary = [
        f"Versão do processamento: {PROCESSING_VERSION}",
        f"Meses na referência: {len(reference.months)}; "
        f"meses com ZIP local processado e referência: {comparable}",
        f"Meses reproduzidos (mesmo SHA-256, mesmas contagens e mesmos valores): {reproduced}",
        "Consistência interna da referência (manifesto e CSV de detalhe; não são dados locais):",
        f"  notas (soma do manifesto): {reference.notes_total}",
        f"  itens (soma do manifesto): {reference.items_total}",
        f"  combinações ano/UF/NCM/CFOP/unidade (linhas do CSV): {reference.detail_rows}",
        f"  itens no CSV de detalhe: {reference.detail_items}",
        f"  valor dos itens no CSV de detalhe: {_fmt_money(reference.detail_value_cents)}",
    ]
    report.summary += _year_comparison(store, reference, reproduced_months)
    report.reproduced = bool(reference.months) and reproduced == len(reference.months)
    if comparable == 0:
        report.summary.append(
            "LIMITE: nenhum ZIP mensal oficial com referência foi processado localmente; os "
            "totais da referência NÃO foram reproduzidos e não se alega reprodução."
        )
    elif not report.reproduced:
        missing = len(reference.months) - reproduced
        report.summary.append(
            f"LIMITE: reprodução parcial. {missing} dos {len(reference.months)} meses da "
            "referência não estão reproduzidos (ZIP ausente, arquivo diferente ou divergência); "
            "os totais gerais da referência NÃO foram reproduzidos."
        )
    else:
        report.summary.append("Todos os meses da referência foram reproduzidos.")
    return report


def _year_comparison(store: Store, reference: Reference, reproduced: set[str]) -> list[str]:
    """Year totals of the detail CSV, compared only when every reference month of the year is
    reproduced locally (otherwise the sets of months differ and the comparison would be wrong)."""
    lines = ["Totais anuais do CSV de detalhe da referência:"]
    for year, (ref_items, ref_cents) in sorted(reference.detail_by_year.items()):
        year_months = {m for m in reference.months if m.startswith(year)}
        if not year_months <= reproduced:
            lines.append(
                f"  {year}: NÃO COMPARÁVEL (meses da referência sem reprodução local: "
                f"{', '.join(sorted(year_months - reproduced)) or 'nenhum'})"
            )
            continue
        marks = ",".join("?" for _ in year_months)
        local_items, local_cents = store.conn.execute(
            f"SELECT COALESCE(SUM(itens),0), COALESCE(SUM(valor_cents),0) FROM agg_item "  # noqa: S608
            f"WHERE month IN ({marks})",
            tuple(sorted(year_months)),
        ).fetchone()
        same = (int(local_items), int(local_cents)) == (ref_items, ref_cents)
        lines.append(
            f"  {year}: {'IGUAL' if same else 'DIVERGENTE'} - referência {ref_items} itens / "
            f"{_fmt_money(ref_cents)}; local {local_items} itens / {_fmt_money(int(local_cents))}"
        )
    return lines
