"""Month processing: stream the tables of a validated ZIP, aggregate, audit and store.

The full row content is never copied out of the bronze ZIP. What is stored is what the reports need:
aggregates by the requested dimensions, one digest per accepted key (to find duplicates between
months), the quarantine with file and line, and the audit of each month. Identifiers of people and
companies (CPF/CNPJ, names) are not read into the store.
"""

from __future__ import annotations

import heapq
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal, localcontext

from sirta_api.adapters.ingest.cgu_nfe.reader import (
    TableFormat,
    find_tables,
    iter_rows,
)
from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.adapters.ingest.cgu_nfe.zipcheck import sha256_file
from sirta_api.domain.cgu_nfe import (
    KIND_EVENT,
    KIND_ITEM,
    KIND_NOTE,
    PROCESSING_VERSION,
    SIT_NO_NOTE,
    SIT_NOTE_QUARANTINED,
    UFS,
    CguNfeError,
    SchemaError,
    ValueRefused,
    access_key_dv_ok,
    classify_situation,
    clean_identifier,
    fingerprint,
    is_access_key,
    item_digest,
    key_digest,
    month_of,
    parse_date,
    parse_decimal,
    to_cents,
)

QUARANTINE_CAP = 5000
DIFF_SAMPLE = 200
MIN_IN_MONTH_SHARE = 0.5

OK, ALERT, FAIL, INFO = "OK", "ALERTA", "FALHA", "INFO"


class ProcessingError(CguNfeError):
    pass


@dataclass
class ProcessOutcome:
    month: str
    status: str  # CONCLUIDO | JA_PROCESSADO | ERRO
    detail: str = ""
    counts: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class _Note:
    fp: bytes
    uf: str
    municipio: str
    uf_dest: str
    cents: int | None
    latest_event: str
    line: int
    member: str


@dataclass(slots=True)
class _ItemContribution:
    fp: bytes
    agg_key: tuple[str, str, str, str, str]  # uf, ncm, cfop, unidade, situacao
    quantity: Decimal | None
    cents: int | None
    note_key: str
    tipo: tuple[str, str] | None
    line: int
    member: str


class _Run:
    def __init__(self, month: str, archive: zipfile.ZipFile, tables: dict[str, list[TableFormat]]):
        self.month = month
        self.archive = archive
        self.tables = tables
        self.alerts: Counter[str] = Counter()
        self.read: Counter[str] = Counter()
        self.quarantine_rows: list[tuple] = []
        self.quarantine_counts: Counter[str] = Counter()
        self.events: dict[str, set[str]] = {}
        self.notes: dict[str, _Note] = {}
        self.note_conflicts: set[str] = set()
        self.note_quarantined: set[str] = set()
        self.note_identical_dups = 0
        self.items: dict[bytes, _ItemContribution] = {}
        self.item_conflicts: set[bytes] = set()
        self.item_identical_dups = 0
        self.agg_item: dict[tuple, list] = {}  # key -> [itens, sem_qtd, sem_valor, qty, cents]
        self.note_items: dict[str, list[int]] = {}  # key -> [cents, itens, itens_sem_valor]
        self.ncm_tipo: Counter[tuple[str, str]] = Counter()
        self.note_in_month = 0
        self.note_with_date = 0

    # -- quarantine --------------------------------------------------------------------------
    def quarantine(
        self,
        kind: str,
        member: str,
        line: int | None,
        reason: str,
        *,
        key: str | None = None,
        item_number: str | None = None,
        detail: str | None = None,
    ) -> None:
        self.quarantine_counts[reason] += 1
        if self.quarantine_counts[reason] > QUARANTINE_CAP:
            return
        masked = key_digest(key).hex() if key and is_access_key(key) else None
        self.quarantine_rows.append(
            (self.month, kind, member, line, reason, masked, item_number, detail)
        )

    # -- helpers -----------------------------------------------------------------------------
    @staticmethod
    def _get(row: list[str], index: dict[str, int], name: str) -> str:
        position = index.get(name)
        return row[position] if position is not None and position < len(row) else ""

    def _check_date(self, text: str, kind: str, counter: str) -> None:
        try:
            day = parse_date(text)
        except ValueRefused:
            self.alerts[f"{kind}_DATA_INVALIDA"] += 1
            return
        if day is None:
            self.alerts[f"{kind}_DATA_AUSENTE"] += 1
        elif month_of(day) != self.month:
            self.alerts[counter] += 1

    # -- events ------------------------------------------------------------------------------
    def read_events(self) -> None:
        for table in self.tables[KIND_EVENT]:
            index, width = table.mapping.index, table.mapping.width
            for line, row in iter_rows(self.archive, table):
                self.read[KIND_EVENT] += 1
                if len(row) != width:
                    self.quarantine(KIND_EVENT, table.member, line, "LINHA_MALFORMADA")
                    continue
                key = clean_identifier(self._get(row, index, "chave"))
                if not is_access_key(key):
                    self.quarantine(KIND_EVENT, table.member, line, "CHAVE_INVALIDA")
                    continue
                text = self._get(row, index, "evento").strip()
                if not text:
                    self.alerts["EVENTO_VAZIO"] += 1
                    continue
                self.events.setdefault(key, set()).add(text)

    # -- notes -------------------------------------------------------------------------------
    def read_notes(self) -> None:
        for table in self.tables[KIND_NOTE]:
            index, width = table.mapping.index, table.mapping.width
            for line, row in iter_rows(self.archive, table):
                self.read[KIND_NOTE] += 1
                if len(row) != width:
                    self.quarantine(KIND_NOTE, table.member, line, "LINHA_MALFORMADA")
                    continue
                key = clean_identifier(self._get(row, index, "chave"))
                if not is_access_key(key):
                    self.quarantine(KIND_NOTE, table.member, line, "CHAVE_INVALIDA")
                    continue
                if not access_key_dv_ok(key):
                    self.alerts["NOTA_CHAVE_DV_DIVERGENTE"] += 1
                try:
                    cents = to_cents(parse_decimal(self._get(row, index, "valor_nota")))
                except ValueRefused as error:
                    self.note_quarantined.add(key)
                    self.quarantine(
                        KIND_NOTE,
                        table.member,
                        line,
                        "VALOR_NOTA_INVALIDO",
                        key=key,
                        detail=str(error),
                    )
                    continue
                if cents is None:
                    self.alerts["NOTA_VALOR_AUSENTE"] += 1
                date_text = self._get(row, index, "data_emissao")
                self._check_date(date_text, "NOTA", "NOTA_DATA_FORA_DO_MES")
                try:
                    day = parse_date(date_text)
                except ValueRefused:
                    day = None
                if day is not None:
                    self.note_with_date += 1
                    self.note_in_month += int(month_of(day) == self.month)
                uf = self._get(row, index, "uf_emitente").strip()
                if uf not in UFS:
                    self.alerts["NOTA_UF_EMITENTE_FORA_DA_LISTA" if uf else "NOTA_UF_AUSENTE"] += 1
                municipio = self._get(row, index, "municipio_emitente").strip()
                if not municipio:
                    self.alerts["NOTA_MUNICIPIO_AUSENTE"] += 1
                record = _Note(
                    fingerprint(row),
                    uf,
                    municipio,
                    self._get(row, index, "uf_destinatario").strip(),
                    cents,
                    self._get(row, index, "evento_recente"),
                    line,
                    table.member,
                )
                self._register_note(key, record)

    def _register_note(self, key: str, record: _Note) -> None:
        if key in self.note_conflicts:
            self.quarantine(
                KIND_NOTE, record.member, record.line, "CHAVE_DUPLICADA_CONFLITANTE", key=key
            )
            return
        previous = self.notes.get(key)
        if previous is None:
            self.notes[key] = record
        elif previous.fp == record.fp:
            self.note_identical_dups += 1
        else:
            self.note_conflicts.add(key)
            self.note_quarantined.add(key)
            del self.notes[key]
            for copy in (previous, record):
                self.quarantine(
                    KIND_NOTE, copy.member, copy.line, "CHAVE_DUPLICADA_CONFLITANTE", key=key
                )

    # -- items -------------------------------------------------------------------------------
    def _situation_of(self, key: str) -> str:
        note = self.notes.get(key)
        if note is not None:
            return classify_situation(note.latest_event, self.events.get(key, set()))
        if key in self.note_quarantined:
            return SIT_NOTE_QUARANTINED
        return SIT_NO_NOTE

    def read_items(self) -> None:
        for table in self.tables[KIND_ITEM]:
            index, width = table.mapping.index, table.mapping.width
            for line, row in iter_rows(self.archive, table):
                self.read[KIND_ITEM] += 1
                if len(row) != width:
                    self.quarantine(KIND_ITEM, table.member, line, "LINHA_MALFORMADA")
                    continue
                self._read_item(table, index, line, row)

    def _read_item(self, table: TableFormat, index: dict[str, int], line: int, row: list[str]):
        member = table.member
        key = clean_identifier(self._get(row, index, "chave"))
        if not is_access_key(key):
            self.quarantine(KIND_ITEM, member, line, "CHAVE_INVALIDA")
            return
        number = clean_identifier(self._get(row, index, "numero_produto"))
        if not number:
            self.quarantine(KIND_ITEM, member, line, "NUMERO_ITEM_AUSENTE", key=key)
            return
        try:
            cents = to_cents(parse_decimal(self._get(row, index, "valor_total")))
        except ValueRefused as error:
            self.quarantine(
                KIND_ITEM,
                member,
                line,
                "VALOR_ITEM_INVALIDO",
                key=key,
                item_number=number,
                detail=str(error),
            )
            return
        try:
            quantity = parse_decimal(self._get(row, index, "quantidade"))
        except ValueRefused as error:
            self.quarantine(
                KIND_ITEM,
                member,
                line,
                "QUANTIDADE_INVALIDA",
                key=key,
                item_number=number,
                detail=str(error),
            )
            return
        digest = item_digest(key, number)
        fp = fingerprint(row)
        if digest in self.item_conflicts:
            self.quarantine(
                KIND_ITEM, member, line, "ITEM_DUPLICADO_CONFLITANTE", key=key, item_number=number
            )
            return
        previous = self.items.get(digest)
        if previous is not None:
            if previous.fp == fp:
                self.item_identical_dups += 1
                return
            self._remove_item(digest, previous)
            self.item_conflicts.add(digest)
            for copy_member, copy_line in ((previous.member, previous.line), (member, line)):
                self.quarantine(
                    KIND_ITEM,
                    copy_member,
                    copy_line,
                    "ITEM_DUPLICADO_CONFLITANTE",
                    key=key,
                    item_number=number,
                )
            return

        self._item_alerts(row, index, key, cents, quantity)
        uf = self._get(row, index, "uf_emitente").strip()
        ncm = clean_identifier(self._get(row, index, "ncm"))
        cfop = clean_identifier(self._get(row, index, "cfop"))
        unit = self._get(row, index, "unidade").strip()
        tipo_text = self._get(row, index, "ncm_tipo").strip()
        agg_key = (uf, ncm, cfop, unit, self._situation_of(key))
        tipo = (ncm, tipo_text) if "ncm_tipo" in index else None
        contribution = _ItemContribution(fp, agg_key, quantity, cents, key, tipo, line, member)
        self.items[digest] = contribution
        self._apply(contribution, +1)

    def _item_alerts(
        self, row: list[str], index: dict[str, int], key: str, cents: int | None, quantity
    ) -> None:
        self._check_date(self._get(row, index, "data_emissao"), "ITEM", "ITEM_DATA_FORA_DO_MES")
        uf = self._get(row, index, "uf_emitente").strip()
        if not uf:
            self.alerts["ITEM_UF_AUSENTE"] += 1
        elif uf not in UFS:
            self.alerts["ITEM_UF_EMITENTE_FORA_DA_LISTA"] += 1
        if not self._get(row, index, "municipio_emitente").strip():
            self.alerts["ITEM_MUNICIPIO_AUSENTE"] += 1
        if not clean_identifier(self._get(row, index, "ncm")):
            self.alerts["ITEM_NCM_AUSENTE"] += 1
        if not clean_identifier(self._get(row, index, "cfop")):
            self.alerts["ITEM_CFOP_AUSENTE"] += 1
        if not self._get(row, index, "unidade").strip():
            self.alerts["ITEM_UNIDADE_AUSENTE"] += 1
        if quantity is None:
            self.alerts["ITEM_QUANTIDADE_AUSENTE"] += 1
        if cents is None:
            self.alerts["ITEM_VALOR_AUSENTE"] += 1
        note = self.notes.get(key)
        if note is not None and uf and note.uf and uf != note.uf:
            self.alerts["ITEM_UF_DIFERENTE_DA_NOTA"] += 1

    def _apply(self, c: _ItemContribution, sign: int) -> None:
        slot = self.agg_item.setdefault(c.agg_key, [0, 0, 0, Decimal(0), 0])
        slot[0] += sign
        if c.quantity is None:
            slot[1] += sign
        else:
            slot[3] += c.quantity if sign > 0 else -c.quantity
        if c.cents is None:
            slot[2] += sign
        else:
            slot[4] += sign * c.cents
        per_note = self.note_items.setdefault(c.note_key, [0, 0, 0])
        per_note[1] += sign
        if c.cents is None:
            per_note[2] += sign
        else:
            per_note[0] += sign * c.cents
        if c.tipo is not None:
            self.ncm_tipo[c.tipo] += sign

    def _remove_item(self, digest: bytes, contribution: _ItemContribution) -> None:
        self._apply(contribution, -1)
        del self.items[digest]


def _align(archive: zipfile.ZipFile) -> dict[str, list[TableFormat]]:
    tables = find_tables(archive)
    missing = [k for k in (KIND_NOTE, KIND_ITEM) if not tables[k]]
    if missing:
        raise SchemaError(f"ZIP sem as tabelas obrigatórias: {', '.join(missing)}")
    return tables


def _situations_and_notes(run: _Run):
    """Aggregates of notes by (UF, municipality) and (UF, destination UF), with the situation."""
    by_city: dict[tuple, list[int]] = {}
    by_dest: dict[tuple, list[int]] = {}
    for key, note in run.notes.items():
        situation = classify_situation(note.latest_event, run.events.get(key, set()))
        for bucket, dims in (
            (by_city, (note.uf, note.municipio, situation)),
            (by_dest, (note.uf, note.uf_dest, situation)),
        ):
            slot = bucket.setdefault(dims, [0, 0, 0])
            slot[0] += 1
            if note.cents is None:
                slot[1] += 1
            else:
                slot[2] += note.cents
    return by_city, by_dest


def _reconcile(run: _Run):
    """Note value versus the sum of its items. A difference is recorded, not concluded upon."""
    with_items = without_items = with_diff = abs_sum = net_sum = 0
    heap: list[tuple[int, str, int, int, int, str, int, int]] = []
    for key, note in run.notes.items():
        sums = run.note_items.get(key)
        if not sums or sums[1] <= 0:
            without_items += 1
            continue
        with_items += 1
        if note.cents is None:
            continue
        diff = note.cents - sums[0]
        if diff == 0:
            continue
        with_diff += 1
        abs_sum += abs(diff)
        net_sum += diff
        entry = (
            abs(diff),
            key_digest(key).hex(),
            diff,
            note.cents,
            sums[0],
            note.member,
            note.line,
            sums[1],
        )
        if len(heap) < DIFF_SAMPLE:
            heapq.heappush(heap, entry)
        elif entry > heap[0]:
            heapq.heapreplace(heap, entry)
    sample = sorted(heap, reverse=True)
    return with_items, without_items, with_diff, abs_sum, net_sum, sample


def process_month(
    store: Store,
    month: str,
    *,
    force: bool = False,
    version: str = PROCESSING_VERSION,
) -> ProcessOutcome:
    file = store.current_file(month)
    if file is None:
        return ProcessOutcome(month, "ERRO", "sem arquivo validado para o mês")
    sha = file["sha256"]
    if not force and store.completed_processing(month, sha, version):
        return ProcessOutcome(month, "JA_PROCESSADO", "mesmo sha256 e mesma versão")
    path = store.bronze_path(month)
    if not path.is_file() or sha256_file(path) != sha:
        store.set_invalid(month, "arquivo do bronze ausente ou diferente do manifesto")
        return ProcessOutcome(month, "ERRO", "bronze diferente do manifesto")
    processing_id = store.start_processing(month, file["id"], sha, version)
    try:
        with localcontext() as ctx, zipfile.ZipFile(path) as archive:
            ctx.prec = 60
            counts = _process(store, month, archive, file["id"], processing_id)
    except (CguNfeError, zipfile.BadZipFile, UnicodeDecodeError) as error:
        store.finish_processing(processing_id, "ERRO", None, str(error))
        store.set_invalid(month, f"processamento recusado: {error}")
        return ProcessOutcome(month, "ERRO", str(error))
    store.finish_processing(processing_id, "CONCLUIDO", counts, None)
    store.set_invalid(month, None)
    return ProcessOutcome(month, "CONCLUIDO", "", counts)


def _process(
    store: Store, month: str, archive: zipfile.ZipFile, file_id: int, processing_id: int
) -> dict[str, int]:
    tables = _align(archive)
    run = _Run(month, archive, tables)
    run.read_events()
    run.read_notes()
    run.read_items()

    if run.note_with_date and run.note_in_month / run.note_with_date < MIN_IN_MONTH_SHARE:
        raise ProcessingError(
            f"Os dados não pertencem ao mês {month}: {run.note_in_month} de "
            f"{run.note_with_date} notas com data no mês"
        )
    by_city, by_dest = _situations_and_notes(run)
    with_items, without_items, with_diff, abs_sum, net_sum, sample = _reconcile(run)

    accepted_notes = len(run.notes)
    accepted_items = len(run.items)
    note_value = sum(n.cents or 0 for n in run.notes.values())
    item_value = sum(c.cents or 0 for c in run.items.values())
    orphan_items = sum(
        1 for c in run.items.values() if c.agg_key[4] in (SIT_NO_NOTE, SIT_NOTE_QUARANTINED)
    )
    cancelled = sum(1 for n in run.notes if _is_cancelled(run, n))
    orphan_events = sum(1 for k in run.events if k not in run.notes and k not in run.note_conflicts)

    note_keys = [(key_digest(k), month, n.fp) for k, n in run.notes.items()]
    item_keys = [(d, month, c.fp) for d, c in run.items.items()]

    with store.transaction() as conn:
        store.clear_month(conn, month)
        cross = _cross_month(conn, month, note_keys, item_keys)
        conn.executemany(
            "INSERT INTO agg_nota_mun VALUES (?,?,?,?,?,?,?)",
            [(month, *k, *v) for k, v in by_city.items()],
        )
        conn.executemany(
            "INSERT INTO agg_nota_uf_dest VALUES (?,?,?,?,?,?,?)",
            [(month, *k, *v) for k, v in by_dest.items()],
        )
        conn.executemany(
            "INSERT INTO agg_item VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                (month, *k, v[0], v[1], v[2], format(v[3], "f"), v[4])
                for k, v in run.agg_item.items()
                if v[0] != 0
            ],
        )
        conn.executemany(
            "INSERT INTO ncm_tipo VALUES (?,?,?,?)",
            [(month, ncm, tipo, n) for (ncm, tipo), n in run.ncm_tipo.items() if n > 0],
        )
        conn.executemany("INSERT INTO nota_keys VALUES (?,?,?)", note_keys)
        conn.executemany("INSERT INTO item_keys VALUES (?,?,?)", item_keys)
        conn.executemany(
            "INSERT INTO quarentena (month, tabela, membro, linha, motivo, chave, numero_item, "
            "detalhe) VALUES (?,?,?,?,?,?,?,?)",
            run.quarantine_rows,
        )
        conn.executemany(
            "INSERT INTO diferencas (month, chave, membro, linha, valor_nota_cents, "
            "soma_itens_cents, itens, diferenca_cents) VALUES (?,?,?,?,?,?,?,?)",
            [
                (month, digest, member, line, note_cents, items_cents, n_items, diff)
                for _abs, digest, diff, note_cents, items_cents, member, line, n_items in sample
            ],
        )
        conn.execute(
            "INSERT INTO reconc_mes VALUES (?,?,?,?,?,?)",
            (month, with_items, without_items, with_diff, abs_sum, net_sum),
        )
        conn.executemany(
            "INSERT INTO duplicidades_meses VALUES (?,?,?,?,?)",
            [
                (month, tabela, other, ident, conf)
                for (tabela, other), (ident, conf) in cross.items()
            ],
        )

        # Reconciliation of what was stored against what was read, inside the same transaction.
        stored = conn.execute(
            "SELECT COALESCE(SUM(notas),0), COALESCE(SUM(valor_cents),0) FROM agg_nota_mun "
            "WHERE month=?",
            (month,),
        ).fetchone()
        stored_dest = conn.execute(
            "SELECT COALESCE(SUM(notas),0), COALESCE(SUM(valor_cents),0) FROM agg_nota_uf_dest "
            "WHERE month=?",
            (month,),
        ).fetchone()
        stored_items = conn.execute(
            "SELECT COALESCE(SUM(itens),0), COALESCE(SUM(valor_cents),0) FROM agg_item "
            "WHERE month=?",
            (month,),
        ).fetchone()
        checks = {
            "RECONCILIACAO_NOTAS_UF_MUNICIPIO": (accepted_notes, note_value, tuple(stored)),
            "RECONCILIACAO_NOTAS_UF_DESTINO": (accepted_notes, note_value, tuple(stored_dest)),
            "RECONCILIACAO_ITENS": (accepted_items, item_value, tuple(stored_items)),
        }
        audit: list[tuple] = []
        for check_id, (n_expected, v_expected, got) in checks.items():
            ok = got == (n_expected, v_expected)
            audit.append(
                (
                    month,
                    check_id,
                    OK if ok else FAIL,
                    n_expected,
                    f"lido={n_expected}/{v_expected} centavos; gravado={got[0]}/{got[1]}",
                )
            )
            if not ok:
                raise ProcessingError(f"Reconciliação falhou em {check_id}: {got} != {n_expected}")
        audit.extend(
            _audit_rows(
                month,
                run,
                tables,
                accepted_notes,
                accepted_items,
                with_items,
                without_items,
                with_diff,
                orphan_items,
                cancelled,
                orphan_events,
                cross,
            )
        )
        conn.executemany("INSERT INTO auditoria VALUES (?,?,?,?,?)", audit)

    return {
        "notas_lidas": run.read[KIND_NOTE],
        "notas_aceitas": accepted_notes,
        "itens_lidos": run.read[KIND_ITEM],
        "itens_aceitos": accepted_items,
        "eventos_lidos": run.read[KIND_EVENT],
        "valor_notas_centavos": note_value,
        "valor_itens_centavos": item_value,
        "quarentena": sum(run.quarantine_counts.values()),
        "arquivo_id": file_id,
        "processamento_id": processing_id,
    }


def _is_cancelled(run: _Run, key: str) -> bool:
    note = run.notes[key]
    return classify_situation(note.latest_event, run.events.get(key, set())) == "CANCELADA"


def _cross_month(conn, month: str, note_keys: list[tuple], item_keys: list[tuple]) -> dict:
    """Keys that already exist in other months: identical copies and conflicting copies."""
    result: dict[tuple[str, str], tuple[int, int]] = {}
    for tabela, table, keys in (("NOTA", "nota_keys", note_keys), ("ITEM", "item_keys", item_keys)):
        conn.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_keys (digest BLOB, fp BLOB)")
        conn.execute("DELETE FROM tmp_keys")
        conn.executemany("INSERT INTO tmp_keys VALUES (?,?)", [(d, fp) for d, _m, fp in keys])
        rows = conn.execute(
            f"SELECT k.month AS other, COUNT(*) AS n, SUM(k.fp = t.fp) AS same "  # noqa: S608
            f"FROM {table} k JOIN tmp_keys t ON t.digest = k.digest "
            f"WHERE k.month <> ? GROUP BY k.month",
            (month,),
        ).fetchall()
        for row in rows:
            same = int(row["same"] or 0)
            result[(tabela, row["other"])] = (same, int(row["n"]) - same)
        conn.execute("DELETE FROM tmp_keys")
    return result


def _audit_rows(
    month,
    run,
    tables,
    accepted_notes,
    accepted_items,
    with_items,
    without_items,
    with_diff,
    orphan_items,
    cancelled,
    orphan_events,
    cross,
) -> list[tuple]:
    rows: list[tuple] = []

    def add(check_id: str, result: str, quantity: int | None, detail: str = "") -> None:
        rows.append((month, check_id, result, quantity, detail))

    for kind, group in tables.items():
        for table in group:
            fmt_ok = table.matches_expected
            add(
                f"FORMATO_{kind}_{table.member}",
                OK if fmt_ok and table.encoding == "cp1252" else ALERT if not fmt_ok else INFO,
                None,
                f"codificacao={table.encoding}; separador={table.delimiter!r}; bom={table.bom}",
            )
            if table.mapping.unknown:
                add(
                    f"COLUNAS_NAO_MAPEADAS_{kind}_{table.member}",
                    INFO,
                    len(table.mapping.unknown),
                    "; ".join(table.mapping.unknown)[:500],
                )
    if not tables[KIND_EVENT]:
        add("TABELA_EVENTOS_AUSENTE", ALERT, None, "cancelamento só pelo campo de evento recente")
    add("LINHAS_LIDAS_NOTA", INFO, run.read[KIND_NOTE])
    add("LINHAS_LIDAS_ITEM", INFO, run.read[KIND_ITEM])
    add("LINHAS_LIDAS_EVENTO", INFO, run.read[KIND_EVENT])
    add("NOTAS_ACEITAS", INFO, accepted_notes)
    add("ITENS_ACEITOS", INFO, accepted_items)
    add(
        "CHAVE_NOTA_DUPLICADA_IDENTICA",
        INFO if run.note_identical_dups else OK,
        run.note_identical_dups,
        "contada uma vez",
    )
    add(
        "CHAVE_NOTA_DUPLICADA_CONFLITANTE",
        ALERT if run.note_conflicts else OK,
        len(run.note_conflicts),
        "todas as versões em quarentena, fora dos totais",
    )
    add(
        "ITEM_DUPLICADO_IDENTICO",
        INFO if run.item_identical_dups else OK,
        run.item_identical_dups,
        "contado uma vez",
    )
    add(
        "ITEM_DUPLICADO_CONFLITANTE",
        ALERT if run.item_conflicts else OK,
        len(run.item_conflicts),
        "todas as versões em quarentena, fora dos totais",
    )
    add("ITENS_SEM_NOTA", ALERT if orphan_items else OK, orphan_items, "itens sem cabeçalho aceito")
    add("NOTAS_SEM_ITENS", INFO if without_items else OK, without_items)
    add("NOTAS_COM_ITENS", INFO, with_items)
    add(
        "NOTA_DIFERENTE_DA_SOMA_DOS_ITENS",
        INFO if with_diff else OK,
        with_diff,
        "registrado; não indica irregularidade por si só",
    )
    add("NOTAS_CANCELADAS_PELOS_EVENTOS", INFO, cancelled, "regra: evento contém CANCEL")
    add("EVENTOS_SEM_NOTA", INFO if orphan_events else OK, orphan_events)
    for reason, n in sorted(run.quarantine_counts.items()):
        truncated = max(0, n - QUARANTINE_CAP)
        add(
            f"QUARENTENA_{reason}",
            ALERT,
            n,
            f"detalhe gravado para {n - truncated}; {truncated} só contadas" if truncated else "",
        )
    for name, n in sorted(run.alerts.items()):
        add(name, ALERT, n)
    for (tabela, other), (same, conflicting) in sorted(cross.items()):
        add(
            f"CHAVE_{tabela}_TAMBEM_EM_{other}",
            ALERT,
            same + conflicting,
            f"idênticas={same}; conflitantes={conflicting}; mantidas nos dois meses, só reportadas",
        )
    return rows
