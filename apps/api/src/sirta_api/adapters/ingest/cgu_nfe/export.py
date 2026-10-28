"""Gold exports: one workbook with six sheets plus complete CSVs, all from the SQLite store.

Rules kept here:
- Only months whose current ZIP is processed with the current version enter the totals.
- A month without data is ``SEM DADOS`` in the series, never zero. Zero means "processed, nothing".
- Raw totals (all accepted notes and items, cancelled ones included) sit next to the cancelled
  figures and the figures excluding cancelled notes. The raw totals are never silently filtered.
- ``PARCIAL`` stays in the file names until the 60 months are processed.
- The CSVs are exact (integer cents, source precision). The workbook stores numbers as Excel
  numbers (about 15 digits).
- Nothing here claims that the NF-e base is the whole market or all public purchases.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from itertools import groupby
from pathlib import Path

from sirta_api.adapters.ingest.cgu_nfe.inventory import MonthStatus, month_statuses
from sirta_api.adapters.ingest.cgu_nfe.store import Store, now_iso
from sirta_api.adapters.ingest.cgu_nfe.xlsx import (
    Money,
    SheetTooLarge,
    XlsxWriter,
    read_xlsx,
)
from sirta_api.domain.cgu_nfe import (
    CATALOG_URL,
    DICTIONARY_URL,
    PROCESSING_VERSION,
    SIT_CANCELLED,
    SIT_NO_NOTE,
    SIT_NOTE_QUARANTINED,
    STATE_DONE,
    CguNfeError,
    cents_to_text,
    decimal_to_text,
    parse_decimal,
    requested_months,
    to_cents,
)

DEFAULT_PREFIX = "CGU_NFE_2021_2025"
UF_BLANK = "(NAO INFORMADA)"
MUNICIPALITY_BLANK = "(NAO INFORMADO)"
GRAIN_ROW_LIMIT = 1_000_000
SOURCE_REFERENCE = "CGU - Portal da Transparencia, Notas Fiscais (NF-e); arquivos AAAAMM_NFe.zip"
SEM_DADOS = "SEM DADOS"


class ExportError(CguNfeError):
    pass


@dataclass
class ExportFile:
    name: str
    path: Path
    rows: int
    sha256: str = ""


@dataclass
class ExportReport:
    partial: bool
    months_done: list[str]
    months_pending: dict[str, str]
    workbook: ExportFile | None
    csv_files: list[ExportFile] = field(default_factory=list)
    checks: list[tuple[str, str, str]] = field(default_factory=list)  # id, result, detail
    sheet_grain_note: str = ""

    @property
    def ok(self) -> bool:
        return all(result == "OK" for _id, result, _detail in self.checks)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, Money):
        return cents_to_text(value.cents)
    if isinstance(value, Decimal):
        return decimal_to_text(value)
    return str(value)


def _write_csv(path: Path, header: list[str], rows: Iterable[list[object]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", lineterminator="\r\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow([_csv_cell(v) for v in row])
            count += 1
    return count


def _bucket(situation: str) -> str:
    if situation == SIT_CANCELLED:
        return "canc"
    if situation in (SIT_NO_NOTE, SIT_NOTE_QUARANTINED):
        return "orfao"
    return "outros"


class Exporter:
    def __init__(self, store: Store, *, prefix: str = DEFAULT_PREFIX) -> None:
        self.store = store
        self.prefix = prefix
        self.conn = store.conn
        statuses = month_statuses(store)
        self.statuses: list[MonthStatus] = statuses
        self.done = [s.month for s in statuses if s.state == STATE_DONE]
        self.pending = {s.month: s.state for s in statuses if s.state != STATE_DONE}
        self.partial = bool(self.pending)
        self.tag = "PARCIAL" if self.partial else "COMPLETO"

    # -- data views ---------------------------------------------------------------------------
    def _prepare(self) -> None:
        self.conn.execute("CREATE TEMP TABLE IF NOT EXISTS done_months (month TEXT PRIMARY KEY)")
        self.conn.execute("DELETE FROM done_months")
        self.conn.executemany("INSERT INTO done_months VALUES (?)", [(m,) for m in self.done])

    def _months_by_year(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for month in self.done:
            out[month[:4]] = out.get(month[:4], 0) + 1
        return out

    @staticmethod
    def _note_cols(buckets: dict[str, list[int]], per_year_months: int) -> list[object]:
        total = [sum(b[i] for b in buckets.values()) for i in range(3)]
        canc = buckets.get("canc", [0, 0, 0])
        return [
            per_year_months,
            total[0],
            Money(total[2]),
            canc[0],
            Money(canc[2]),
            total[0] - canc[0],
            Money(total[2] - canc[2]),
            total[1],
        ]

    NOTE_HEADER = [
        "Meses com dados no ano",
        "Notas (bruto, inclui canceladas)",
        "Valor das notas (R$, bruto)",
        "Notas canceladas (eventos)",
        "Valor das notas canceladas (R$)",
        "Notas exceto canceladas",
        "Valor das notas exceto canceladas (R$)",
        "Notas sem valor informado",
    ]

    def uf_rows(self) -> Iterator[list[object]]:
        months = self._months_by_year()
        notes: dict[tuple[str, str], dict[str, list[int]]] = {}
        for r in self.conn.execute(
            "SELECT substr(a.month,1,4) ano, a.uf, a.situacao, SUM(a.notas), "
            "SUM(a.notas_sem_valor), SUM(a.valor_cents) FROM agg_nota_mun a "
            "JOIN done_months d USING (month) "
            "GROUP BY ano, a.uf, a.situacao"
        ):
            slot = notes.setdefault((r[0], r[1]), {}).setdefault(_bucket(r[2]), [0, 0, 0])
            slot[0] += r[3]
            slot[1] += r[4]
            slot[2] += r[5]
        items: dict[tuple[str, str], dict[str, list[int]]] = {}
        for r in self.conn.execute(
            "SELECT substr(a.month,1,4) ano, a.uf, a.situacao, SUM(a.itens), SUM(a.valor_cents) "
            "FROM agg_item a JOIN done_months d USING (month) GROUP BY ano, a.uf, a.situacao"
        ):
            slot = items.setdefault((r[0], r[1]), {}).setdefault(_bucket(r[2]), [0, 0])
            slot[0] += r[3]
            slot[1] += r[4]
        for ano, uf in sorted(set(notes) | set(items)):
            nb = notes.get((ano, uf), {})
            ib = items.get((ano, uf), {})
            item_total = [sum(b[i] for b in ib.values()) for i in range(2)]
            canc = ib.get("canc", [0, 0])
            orphan = ib.get("orfao", [0, 0])
            yield [
                ano,
                uf or UF_BLANK,
                *self._note_cols(nb, months.get(ano, 0)),
                item_total[0],
                Money(item_total[1]),
                canc[0],
                Money(canc[1]),
                item_total[0] - canc[0],
                Money(item_total[1] - canc[1]),
                orphan[0],
                SOURCE_REFERENCE,
            ]

    UF_HEADER = [
        "Ano",
        "UF do emitente (origem do fornecedor)",
        *NOTE_HEADER,
        "Itens (bruto, inclui canceladas)",
        "Valor dos itens (R$, bruto)",
        "Itens de notas canceladas",
        "Valor dos itens de notas canceladas (R$)",
        "Itens exceto canceladas",
        "Valor dos itens exceto canceladas (R$)",
        "Itens sem nota aceita (sem cabecalho ou em quarentena)",
        "Fonte",
    ]

    def city_rows(self) -> Iterator[list[object]]:
        months = self._months_by_year()
        cursor = self.conn.execute(
            "SELECT substr(a.month,1,4) ano, a.uf, a.municipio, a.situacao, SUM(a.notas), "
            "SUM(a.notas_sem_valor), SUM(a.valor_cents) FROM agg_nota_mun a "
            "JOIN done_months d USING (month) GROUP BY ano, a.uf, a.municipio, a.situacao "
            "ORDER BY ano, a.uf, a.municipio"
        )
        for (ano, uf, city), group in groupby(cursor, key=lambda r: (r[0], r[1], r[2])):
            buckets: dict[str, list[int]] = {}
            for r in group:
                slot = buckets.setdefault(_bucket(r[3]), [0, 0, 0])
                slot[0] += r[4]
                slot[1] += r[5]
                slot[2] += r[6]
            yield [
                ano,
                uf or UF_BLANK,
                city or MUNICIPALITY_BLANK,
                *self._note_cols(buckets, months.get(ano, 0)),
                SOURCE_REFERENCE,
            ]

    CITY_HEADER = [
        "Ano",
        "UF do emitente",
        "Município do emitente (grafia original da fonte)",
        *NOTE_HEADER,
        "Fonte",
    ]

    def goods_count(self, *, with_cfop: bool) -> int:
        cols = "substr(a.month,1,4), a.uf, a.ncm, a.unidade" + (", a.cfop" if with_cfop else "")
        row = self.conn.execute(
            f"SELECT COUNT(*) FROM (SELECT DISTINCT {cols} FROM agg_item a "  # noqa: S608
            "JOIN done_months d USING (month))"
        ).fetchone()
        return int(row[0])

    def _ncm_descriptions(self) -> dict[str, str]:
        best: dict[str, tuple[int, str]] = {}
        for ncm, tipo, n in self.conn.execute(
            "SELECT t.ncm, t.tipo, SUM(t.itens) FROM ncm_tipo t JOIN done_months d USING (month) "
            "GROUP BY t.ncm, t.tipo"
        ):
            if tipo and (ncm not in best or n > best[ncm][0]):
                best[ncm] = (n, tipo)
        return {k: v[1] for k, v in best.items()}

    GOODS_HEADER = [
        "Ano",
        "UF do emitente",
        "NCM (código da fonte, texto)",
        "Descrição do NCM/SH (tipo de produto informado na fonte)",
        "CFOP (código da fonte, texto)",
        "Unidade comercial declarada",
        "Itens (bruto)",
        "Quantidade comercial declarada (bruto; só soma a mesma unidade)",
        "Valor dos itens (R$, bruto)",
        "Itens de notas canceladas",
        "Valor itens canceladas (R$)",
        "Itens exceto canceladas",
        "Valor itens exceto canceladas (R$)",
        "Itens sem quantidade",
        "Itens sem valor",
        "Fonte",
    ]

    def goods_rows(self, *, with_cfop: bool = True) -> Iterator[list[object]]:
        descriptions = self._ncm_descriptions()
        order = "ano, a.uf, a.ncm" + (", a.cfop" if with_cfop else "") + ", a.unidade"
        cursor = self.conn.execute(
            "SELECT substr(a.month,1,4) ano, a.uf, a.ncm, a.cfop, a.unidade, a.situacao, a.itens, "
            "a.itens_sem_quantidade, a.itens_sem_valor, a.quantidade, a.valor_cents "
            f"FROM agg_item a JOIN done_months d USING (month) ORDER BY {order}"  # noqa: S608
        )

        def key(r):
            return (r[0], r[1], r[2], r[3] if with_cfop else "", r[4])

        with localcontext() as ctx:
            ctx.prec = 60
            for (ano, uf, ncm, cfop, unit), group in groupby(cursor, key=key):
                total_n = total_c = canc_n = canc_c = no_qty = no_val = 0
                quantity = Decimal(0)
                for r in group:
                    total_n += r[6]
                    no_qty += r[7]
                    no_val += r[8]
                    quantity += Decimal(r[9])
                    total_c += r[10]
                    if r[5] == SIT_CANCELLED:
                        canc_n += r[6]
                        canc_c += r[10]
                yield [
                    ano,
                    uf or UF_BLANK,
                    ncm,
                    descriptions.get(ncm, ""),
                    cfop if with_cfop else "(não detalhado nesta aba)",
                    unit,
                    total_n,
                    quantity,
                    Money(total_c),
                    canc_n,
                    Money(canc_c),
                    total_n - canc_n,
                    Money(total_c - canc_c),
                    no_qty,
                    no_val,
                    SOURCE_REFERENCE,
                ]

    def series_rows(self) -> Iterator[list[object]]:
        notes = {
            r[0]: (r[1], r[2], r[3])
            for r in self.conn.execute(
                "SELECT month, SUM(notas), SUM(valor_cents), SUM(notas_sem_valor) "
                "FROM agg_nota_mun JOIN done_months USING (month) GROUP BY month"
            )
        }
        canc = {
            r[0]: (r[1], r[2])
            for r in self.conn.execute(
                "SELECT month, SUM(notas), SUM(valor_cents) FROM agg_nota_mun "
                "JOIN done_months USING (month) WHERE situacao=? GROUP BY month",
                (SIT_CANCELLED,),
            )
        }
        items = {
            r[0]: (r[1], r[2])
            for r in self.conn.execute(
                "SELECT month, SUM(itens), SUM(valor_cents) FROM agg_item "
                "JOIN done_months USING (month) GROUP BY month"
            )
        }
        counts = {
            r["month"]: r["counts"]
            for r in self.conn.execute(
                "SELECT month, counts FROM processamentos WHERE status='CONCLUIDO' ORDER BY id"
            )
        }
        for status in self.statuses:
            month = status.month
            base = [month, month[:4], month[4:], status.state]
            if status.state != STATE_DONE:
                reason = status.detail or {
                    "NAO_LISTADO": "mês não listado no catálogo da fonte",
                    "DOWNLOAD_PENDENTE": "arquivo listado, ainda não obtido",
                }.get(status.state, status.state)
                yield [*base, SEM_DADOS, reason] + [SEM_DADOS] * 9 + [status.url]
                continue
            n, v, sv = notes.get(month, (0, 0, 0))
            cn, cv = canc.get(month, (0, 0))
            i, iv = items.get(month, (0, 0))
            detail = json.loads(counts.get(month) or "{}")
            yield [
                *base,
                "COM DADOS",
                "",
                n,
                Money(v),
                cn,
                Money(cv),
                n - cn,
                Money(v - cv),
                i,
                Money(iv),
                detail.get("quarentena", 0),
                status.url,
            ]

    SERIES_HEADER = [
        "Mês (AAAAMM)",
        "Ano",
        "Mês",
        "Estado do mês",
        "Cobertura",
        "Motivo da ausência",
        "Notas (bruto)",
        "Valor das notas (R$, bruto)",
        "Notas canceladas (eventos)",
        "Valor notas canceladas (R$)",
        "Notas exceto canceladas",
        "Valor notas exceto canceladas (R$)",
        "Itens (bruto)",
        "Valor dos itens (R$, bruto)",
        "Linhas em quarentena",
        "URL do arquivo",
    ]

    def audit_rows(self) -> Iterator[list[object]]:
        for status in self.statuses:
            if status.state != STATE_DONE:
                detail = f"{status.state} {status.detail}".strip()
                yield [status.month, "COBERTURA_DO_MES", "PENDENTE", None, detail]
        for r in self.conn.execute(
            "SELECT a.month, a.check_id, a.resultado, a.quantidade, a.detalhe FROM auditoria a "
            "JOIN done_months d USING (month) ORDER BY a.month, a.resultado, a.check_id"
        ):
            yield list(r)

    AUDIT_HEADER = ["Mês (AAAAMM)", "Verificação", "Resultado", "Quantidade", "Detalhe"]

    def manifest_rows(self) -> Iterator[list[object]]:
        for status in self.statuses:
            file = self.store.current_file(status.month)
            processing = self.store.latest_processing(status.month)
            yield [
                status.month,
                status.state,
                "SIM" if status.listed else "NAO",
                status.url,
                (file["url_used"] if file and file["url_used"] else ""),
                file["origem"] if file else "",
                file["acquired_at"] if file else "",
                file["size"] if file else None,
                file["sha256"] if file else "",
                (
                    ""
                    if not file or file["reference_match"] is None
                    else ("SIM" if file["reference_match"] else "NAO")
                ),
                status.head_status,
                status.head_size,
                processing["version"] if processing else "",
                processing["finished_at"] if processing else "",
            ]

    MANIFEST_HEADER = [
        "Mês (AAAAMM)",
        "Estado",
        "Listado no catálogo",
        "URL oficial do arquivo",
        "URL efetivamente usada no download",
        "Origem do arquivo",
        "Data da aquisição (UTC)",
        "Tamanho (bytes)",
        "SHA-256",
        "Igual ao hash da referência anterior",
        "HEAD HTTP",
        "HEAD tamanho (bytes)",
        "Versão do processamento",
        "Processado em (UTC)",
    ]

    def quarantine_rows(self) -> Iterator[list[object]]:
        for r in self.conn.execute(
            "SELECT q.month, q.tabela, q.membro, q.linha, q.motivo, q.chave, q.numero_item, "
            "q.detalhe FROM quarentena q JOIN done_months d USING (month) "
            "ORDER BY q.month, q.motivo, q.membro, q.linha"
        ):
            yield list(r)

    QUARANTINE_HEADER = [
        "Mês (AAAAMM)",
        "Tabela",
        "Arquivo no ZIP",
        "Linha",
        "Motivo",
        "Digest da chave (blake2b-16, hex)",
        "Número do item",
        "Detalhe",
    ]

    def difference_rows(self) -> Iterator[list[object]]:
        for r in self.conn.execute(
            "SELECT x.month, x.chave, x.membro, x.linha, x.valor_nota_cents, x.soma_itens_cents, "
            "x.itens, x.diferenca_cents FROM diferencas x JOIN done_months d USING (month) "
            "ORDER BY x.month, ABS(x.diferenca_cents) DESC"
        ):
            yield [r[0], r[1], r[2], r[3], Money(r[4]), Money(r[5]), r[6], Money(r[7])]

    DIFFERENCE_HEADER = [
        "Mês (AAAAMM)",
        "Digest da chave",
        "Arquivo no ZIP",
        "Linha da nota",
        "Valor da nota (R$)",
        "Soma dos itens (R$)",
        "Itens",
        "Diferença nota menos itens (R$)",
    ]

    # -- totals -------------------------------------------------------------------------------
    def database_totals(self) -> dict[str, int]:
        notes = self.conn.execute(
            "SELECT COALESCE(SUM(notas),0), COALESCE(SUM(valor_cents),0) FROM agg_nota_mun "
            "JOIN done_months USING (month)"
        ).fetchone()
        items = self.conn.execute(
            "SELECT COALESCE(SUM(itens),0), COALESCE(SUM(valor_cents),0) FROM agg_item "
            "JOIN done_months USING (month)"
        ).fetchone()
        return {
            "notas": int(notes[0]),
            "valor_notas_centavos": int(notes[1]),
            "itens": int(items[0]),
            "valor_itens_centavos": int(items[1]),
        }

    # -- run ----------------------------------------------------------------------------------
    def run(self, out_dir: Path | None = None) -> ExportReport:
        if not self.done:
            raise ExportError(
                "nenhum mês processado: nada a exportar. Importe ou baixe ZIPs oficiais e rode "
                "`process` antes."
            )
        out_dir = Path(out_dir or self.store.exports)
        out_dir.mkdir(parents=True, exist_ok=True)
        self._prepare()
        base = f"{self.prefix}_{self.tag}"
        report = ExportReport(self.partial, list(self.done), dict(self.pending), None)

        with_cfop = self.goods_count(with_cfop=True) <= GRAIN_ROW_LIMIT
        if with_cfop:
            report.sheet_grain_note = "Ano, UF, NCM, CFOP e unidade"
        else:
            report.sheet_grain_note = (
                "Ano, UF, NCM e unidade (CFOP omitido na aba por causa do limite de linhas do "
                "Excel; o CSV completo traz o CFOP)"
            )

        datasets = [
            ("por_uf", self.UF_HEADER, self.uf_rows),
            ("municipios", self.CITY_HEADER, self.city_rows),
            ("bens_servicos_completo", self.GOODS_HEADER, lambda: self.goods_rows(with_cfop=True)),
            ("serie_historica", self.SERIES_HEADER, self.series_rows),
            ("auditoria", self.AUDIT_HEADER, self.audit_rows),
            ("manifesto_arquivos", self.MANIFEST_HEADER, self.manifest_rows),
            ("quarentena", self.QUARANTINE_HEADER, self.quarantine_rows),
            ("notas_diferenca_itens", self.DIFFERENCE_HEADER, self.difference_rows),
        ]
        for name, header, rows in datasets:
            path = out_dir / f"{base}_{name}.csv"
            count = _write_csv(path, header, rows())
            report.csv_files.append(ExportFile(name, path, count, _sha256(path)))
        self._verify_csvs(report)

        workbook_path = out_dir / f"{base}.xlsx"
        self._write_workbook(workbook_path, report, with_cfop)
        report.workbook = ExportFile("xlsx", workbook_path, 0, _sha256(workbook_path))
        self._verify_workbook(report)

        checks_path = out_dir / f"{base}_reconciliacao_exportacao.csv"
        count = _write_csv(
            checks_path,
            ["Verificação", "Resultado", "Detalhe"],
            ([c, r, d] for c, r, d in report.checks),
        )
        report.csv_files.append(
            ExportFile("reconciliacao_exportacao", checks_path, count, _sha256(checks_path))
        )
        if not report.ok:
            raise ExportError(
                "reconciliação da exportação falhou: "
                + "; ".join(f"{c}: {d}" for c, r, d in report.checks if r != "OK")
            )
        return report

    # -- workbook -----------------------------------------------------------------------------
    def _coverage_text(self) -> str:
        total = len(requested_months())
        by_state: dict[str, int] = {}
        for state in self.pending.values():
            by_state[state] = by_state.get(state, 0) + 1
        pending = "; ".join(f"{n} {s}" for s, n in sorted(by_state.items())) or "nenhum"
        label = "PARCIAL" if self.partial else "COMPLETA"
        return (
            f"COBERTURA {label}: {len(self.done)} de {total} meses processados. "
            f"Pendências: {pending}. Mês sem dados não é zero."
        )

    def _preface(self, extra: str = "") -> list[list[object]]:
        lines: list[list[object]] = [[self._coverage_text()]]
        lines.append(
            [
                "Base: notas fiscais eletrônicas (NF-e) do portal da CGU. Não representa todo o "
                "mercado, todas as compras públicas nem NFS-e. Valor de nota não é pagamento."
            ]
        )
        if extra:
            lines.append([extra])
        return lines

    def _write_workbook(self, path: Path, report: ExportReport, with_cfop: bool) -> None:
        with XlsxWriter(path) as book:
            book.add_sheet(
                "Consolidado por UF",
                self.uf_rows(),
                header=self.UF_HEADER,
                widths=[8, 16] + [18] * (len(self.UF_HEADER) - 2),
                title="Consolidado por UF do emitente",
                preface=self._preface(),
            )
            book.add_sheet(
                "Municípios",
                self.city_rows(),
                header=self.CITY_HEADER,
                widths=[8, 8, 40] + [18] * (len(self.CITY_HEADER) - 3),
                title="Município do emitente (local do fornecedor, não do consumo ou entrega)",
                preface=self._preface(
                    "Grafia do municipio preservada como na fonte; variantes aparecem em linhas "
                    "separadas."
                ),
            )
            goods_note = f"Granularidade desta aba: {report.sheet_grain_note}."
            try:
                book.add_sheet(
                    "Bens e serviços",
                    self.goods_rows(with_cfop=with_cfop),
                    header=self.GOODS_HEADER,
                    widths=[8, 8, 14, 40, 10, 12] + [18] * (len(self.GOODS_HEADER) - 6),
                    title="Bens e serviços por NCM, CFOP e unidade comercial",
                    preface=self._preface(
                        goods_note
                        + " Quantidade é a declarada comercialmente: não é quantidade física "
                        "padronizada e não se soma entre unidades. O mesmo NCM e unidade pode "
                        "agrupar produtos distintos. Detalhe completo no CSV."
                    ),
                )
            except SheetTooLarge as error:  # pragma: no cover - guarded by GRAIN_ROW_LIMIT
                raise ExportError(
                    f"aba Bens e serviços acima do limite do Excel: {error}"
                ) from error
            book.add_sheet(
                "Série histórica",
                self.series_rows(),
                header=self.SERIES_HEADER,
                widths=[12, 8, 6, 26, 12, 40] + [18] * (len(self.SERIES_HEADER) - 6),
                title="Série histórica mensal (60 meses)",
                preface=self._preface(
                    "SEM DADOS indica ausência de arquivo processado; zero só aparece para mês "
                    "processado."
                ),
            )
            book.add_sheet(
                "Auditoria",
                self.audit_rows(),
                header=self.AUDIT_HEADER,
                widths=[12, 52, 12, 14, 80],
                title="Auditoria dos meses processados e pendencias",
                preface=self._preface(),
            )
            book.add_sheet(
                "Fontes e metodologia",
                self._method_rows(report),
                header=["Item", "Descrição"],
                widths=[38, 120],
                title="Fontes, metodologia e limites",
                preface=self._preface(),
            )

    def _method_rows(self, report: ExportReport) -> Iterator[list[object]]:
        yield ["Catálogo oficial", CATALOG_URL]
        yield ["Dicionário de dados oficial", DICTIONARY_URL]
        yield ["Versão do processamento", PROCESSING_VERSION]
        yield ["Gerado em (UTC)", now_iso()]
        yield ["Granularidade da aba Bens e serviços", report.sheet_grain_note]
        for line in METHOD_LINES:
            yield list(line)
        yield ["Manifesto dos arquivos", "Ver o CSV manifesto_arquivos (hash, URL usada, data)."]
        for row in self.manifest_rows():
            yield [
                f"Arquivo {row[0]}",
                f"estado={row[1]}; origem={row[5] or '-'}; adquirido={row[6] or '-'}; "
                f"sha256={row[8] or '-'}; url={row[4] or row[3]}",
            ]

    # -- verification -------------------------------------------------------------------------
    def _verify_csvs(self, report: ExportReport) -> None:
        db = self.database_totals()
        by_name = {f.name: f for f in report.csv_files}

        def col(path: Path, name: str) -> list[str]:
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle, delimiter=";")
                header = next(reader)
                position = header.index(name)
                return [row[position] for row in reader]

        def cents(values: list[str]) -> int:
            return sum(to_cents(parse_decimal(v)) or 0 for v in values)

        checks = [
            (
                "CSV por_uf: notas",
                sum(int(v) for v in col(by_name["por_uf"].path, self.UF_HEADER[3])),
                db["notas"],
            ),
            (
                "CSV por_uf: valor das notas",
                cents(col(by_name["por_uf"].path, self.UF_HEADER[4])),
                db["valor_notas_centavos"],
            ),
            (
                "CSV municipios: notas",
                sum(int(v) for v in col(by_name["municipios"].path, self.CITY_HEADER[4])),
                db["notas"],
            ),
            (
                "CSV municipios: valor das notas",
                cents(col(by_name["municipios"].path, self.CITY_HEADER[5])),
                db["valor_notas_centavos"],
            ),
            (
                "CSV bens_servicos_completo: itens",
                sum(int(v) for v in col(by_name["bens_servicos_completo"].path, "Itens (bruto)")),
                db["itens"],
            ),
            (
                "CSV bens_servicos_completo: valor dos itens",
                cents(col(by_name["bens_servicos_completo"].path, "Valor dos itens (R$, bruto)")),
                db["valor_itens_centavos"],
            ),
            (
                "CSV serie_historica: notas dos meses com dados",
                sum(
                    int(v)
                    for v in col(by_name["serie_historica"].path, "Notas (bruto)")
                    if v != SEM_DADOS
                ),
                db["notas"],
            ),
        ]
        for name, got, expected in checks:
            ok = got == expected
            report.checks.append(
                (name, "OK" if ok else "FALHA", f"exportado={got}; banco={expected}")
            )
        series_rows = by_name["serie_historica"].rows
        report.checks.append(
            (
                "CSV serie_historica: 60 meses",
                "OK" if series_rows == len(requested_months()) else "FALHA",
                f"linhas={series_rows}",
            )
        )

    def _verify_workbook(self, report: ExportReport) -> None:
        sheets = read_xlsx(report.workbook.path)  # type: ignore[union-attr]
        expected = [
            "Consolidado por UF",
            "Municípios",
            "Bens e serviços",
            "Série histórica",
            "Auditoria",
            "Fontes e metodologia",
        ]
        report.checks.append(
            (
                "XLSX: seis abas na ordem prevista",
                "OK" if list(sheets) == expected else "FALHA",
                ", ".join(sheets),
            )
        )
        db = self.database_totals()

        def table(name: str, first_header: str) -> tuple[list[str], list[list[str]]]:
            rows = sheets[name]
            for i, row in enumerate(rows):
                if row and row[0] == first_header:
                    return row, rows[i + 1 :]
            raise ExportError(f"aba {name} sem cabecalho")

        header, rows = table("Consolidado por UF", "Ano")
        notes = sum(
            int(r[header.index("Notas (bruto, inclui canceladas)")]) for r in rows if len(r) > 3
        )
        value = sum(
            Decimal(r[header.index("Valor das notas (R$, bruto)")])
            for r in rows
            if len(r) > 4 and r[header.index("Valor das notas (R$, bruto)")]
        )
        report.checks.append(
            (
                "XLSX por UF: notas e valor",
                "OK"
                if notes == db["notas"] and int(value * 100) == db["valor_notas_centavos"]
                else "FALHA",
                f"notas={notes}/{db['notas']}; valor={value}/{db['valor_notas_centavos'] / 100}",
            )
        )
        header, rows = table("Série histórica", "Mês (AAAAMM)")
        report.checks.append(
            (
                "XLSX serie histórica: 60 linhas de meses",
                "OK" if len(rows) == len(requested_months()) else "FALHA",
                f"linhas={len(rows)}",
            )
        )
        header, rows = table("Bens e serviços", "Ano")
        goods_items = sum(int(r[header.index("Itens (bruto)")]) for r in rows if len(r) > 6)
        report.checks.append(
            (
                "XLSX bens e serviços: itens",
                "OK" if goods_items == db["itens"] else "FALHA",
                f"itens={goods_items}/{db['itens']}",
            )
        )


METHOD_LINES: list[tuple[str, str]] = [
    (
        "Escopo",
        "NF-e publicadas pela CGU (tabelas de nota, item e evento por mês). Não representa o "
        "mercado inteiro, todas as compras públicas nem NFS-e (serviços municipais).",
    ),
    (
        "Valores",
        "Valor da nota e valor dos itens vem da fonte; são valores de documentos fiscais, não "
        "pagamentos. Em centavos inteiros; valor com mais de duas casas e recusado (quarentena).",
    ),
    (
        "Bruto versus canceladas",
        "O total bruto inclui todas as notas aceitas, canceladas inclusive (mesmo escopo do "
        "levantamento de referência). As colunas de canceladas e de exceto canceladas são "
        "visoes separadas.",
    ),
    (
        "Cancelamento",
        "Nota cancelada = evento mais recente ou algum evento da tabela de eventos contem "
        "CANCEL. Cancelamento é terminal. A regra não prova validade fiscal das demais notas; "
        "nota sem evento informado aparece como SEM_EVENTO_INFORMADO e não como autorizada.",
    ),
    (
        "Local",
        "UF e município são os do emitente (local do fornecedor). A UF do destinatário é outra "
        "dimensao. Não se infere municipio de entrega ou consumo. Grafia preservada.",
    ),
    (
        "Quantidade",
        "Quantidade comercial declarada, com a precisao da fonte. Não e quantidade física "
        "padronizada; não se soma entre unidades nem se convertem embalagens. Mesmo NCM e "
        "unidade podem agrupar produtos distintos.",
    ),
    (
        "Descrição",
        "A descrição do NCM/SH e a informada na fonte (tipo de produto). A descrição comercial "
        "do item não é agregada: permanece no ZIP bronze.",
    ),
    (
        "CFOP",
        "Código mantido como texto. Não se classifica compra ou venda pelo CFOP sem regra "
        "documentada.",
    ),
    (
        "Duplicidades",
        "Copia identica da mesma chave (ou chave+item) conta uma vez e e reportada. Copia "
        "conflitante poe todas as versoes em quarentena, fora dos totais. Chave em mais de um "
        "mês é só reportada.",
    ),
    (
        "Nota versus itens",
        "A soma dos itens não é forçada a igualar o valor da nota. Diferenças ficam em "
        "notas_diferenca_itens (amostra das maiores) e na auditoria, sem concluir irregularidade.",
    ),
    (
        "Itens sem nota",
        "Itens cuja chave não tem nota aceita entram no bruto de itens com a situação "
        "ITEM_SEM_NOTA ou NOTA_EM_QUARENTENA e são contados à parte.",
    ),
    (
        "Excel",
        "Números do Excel guardam cerca de 15 dígitos significativos; os CSVs são a cópia "
        "exata. Códigos (NCM, CFOP) são texto no XLSX; ao abrir CSV no Excel, importe a coluna "
        "como texto para preservar zeros à esquerda.",
    ),
    (
        "Privacidade",
        "CPF/CNPJ e nomes ficam apenas no ZIP bronze local; agregados, quarentena e exportacoes "
        "não os trazem.",
    ),
]
