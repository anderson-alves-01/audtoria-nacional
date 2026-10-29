"""Local SQLite store of the CGU NF-e pipeline (silver) and the layout of the bronze folder.

Layout under the root (default ``<SIRTA_DATALAKE_ROOT>/cgu-nfe``, ignored by Git):

    bronze/AAAAMM_NFe.zip      validated ZIPs, immutable
    bronze/.partial/           downloads in progress (``.part``) and resumable
    bronze/.rejected/          files that failed validation, kept as evidence
    exports/                   generated workbooks and CSVs
    cgu-nfe.sqlite             manifest, monthly aggregates, key indexes, quarantine, audit

The store holds aggregates and key digests, not the full item rows. The original values stay in the
bronze ZIP, whose SHA-256 is in the manifest.

The Simulador in production reads ``cgu-nfe-series.sqlite``: UF × year totals plus processing
metadata. That file has no access keys, names, CPF/CNPJ or bronze ZIPs.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from sirta_api.domain.cgu_nfe import PROCESSING_VERSION, YearUfMeasures

SCHEMA = """
CREATE TABLE IF NOT EXISTS meses (
  month TEXT PRIMARY KEY,
  listed INTEGER NOT NULL DEFAULT 0,
  listed_checked_at TEXT,
  url TEXT NOT NULL,
  head_status INTEGER,
  head_size INTEGER,
  head_checked_at TEXT,
  blocked INTEGER NOT NULL DEFAULT 0,
  blocked_detail TEXT,
  blocked_at TEXT,
  invalid INTEGER NOT NULL DEFAULT 0,
  invalid_detail TEXT
);
CREATE TABLE IF NOT EXISTS arquivos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  size INTEGER NOT NULL,
  origem TEXT NOT NULL,
  url_used TEXT,
  original_path TEXT,
  acquired_at TEXT NOT NULL,
  members TEXT NOT NULL,
  status TEXT NOT NULL,
  reference_sha256 TEXT,
  reference_match INTEGER,
  run_id TEXT,
  UNIQUE (month, sha256)
);
CREATE TABLE IF NOT EXISTS processamentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month TEXT NOT NULL,
  arquivo_id INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  version TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  counts TEXT,
  detail TEXT,
  run_id TEXT
);
CREATE TABLE IF NOT EXISTS agg_nota_mun (
  month TEXT NOT NULL, uf TEXT NOT NULL, municipio TEXT NOT NULL, situacao TEXT NOT NULL,
  notas INTEGER NOT NULL, notas_sem_valor INTEGER NOT NULL, valor_cents INTEGER NOT NULL,
  PRIMARY KEY (month, uf, municipio, situacao)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS agg_nota_uf_dest (
  month TEXT NOT NULL, uf TEXT NOT NULL, uf_dest TEXT NOT NULL, situacao TEXT NOT NULL,
  notas INTEGER NOT NULL, notas_sem_valor INTEGER NOT NULL, valor_cents INTEGER NOT NULL,
  PRIMARY KEY (month, uf, uf_dest, situacao)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS agg_item (
  month TEXT NOT NULL, uf TEXT NOT NULL, ncm TEXT NOT NULL, cfop TEXT NOT NULL,
  unidade TEXT NOT NULL, situacao TEXT NOT NULL,
  itens INTEGER NOT NULL, itens_sem_quantidade INTEGER NOT NULL, itens_sem_valor INTEGER NOT NULL,
  quantidade TEXT NOT NULL, valor_cents INTEGER NOT NULL,
  PRIMARY KEY (month, uf, ncm, cfop, unidade, situacao)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS ncm_tipo (
  month TEXT NOT NULL, ncm TEXT NOT NULL, tipo TEXT NOT NULL, itens INTEGER NOT NULL,
  PRIMARY KEY (month, ncm, tipo)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS auditoria (
  month TEXT NOT NULL, check_id TEXT NOT NULL, resultado TEXT NOT NULL,
  quantidade INTEGER, detalhe TEXT,
  PRIMARY KEY (month, check_id)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS quarentena (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month TEXT NOT NULL, tabela TEXT NOT NULL, membro TEXT NOT NULL, linha INTEGER,
  motivo TEXT NOT NULL, chave TEXT, numero_item TEXT, detalhe TEXT
);
CREATE INDEX IF NOT EXISTS ix_quarentena_month ON quarentena (month, motivo);
CREATE TABLE IF NOT EXISTS diferencas (
  month TEXT NOT NULL, chave TEXT NOT NULL, membro TEXT NOT NULL, linha INTEGER,
  valor_nota_cents INTEGER,
  soma_itens_cents INTEGER NOT NULL, itens INTEGER NOT NULL, diferenca_cents INTEGER NOT NULL,
  PRIMARY KEY (month, chave)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS reconc_mes (
  month TEXT PRIMARY KEY,
  notas_com_itens INTEGER NOT NULL, notas_sem_itens INTEGER NOT NULL,
  notas_com_diferenca INTEGER NOT NULL, soma_abs_diferenca_cents INTEGER NOT NULL,
  soma_liquida_diferenca_cents INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS nota_keys (
  digest BLOB NOT NULL, month TEXT NOT NULL, fp BLOB NOT NULL,
  PRIMARY KEY (digest, month)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS item_keys (
  digest BLOB NOT NULL, month TEXT NOT NULL, fp BLOB NOT NULL,
  PRIMARY KEY (digest, month)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS duplicidades_meses (
  month TEXT NOT NULL, tabela TEXT NOT NULL, outro_mes TEXT NOT NULL,
  identicas INTEGER NOT NULL, conflitantes INTEGER NOT NULL,
  PRIMARY KEY (month, tabela, outro_mes)
) WITHOUT ROWID;
"""

FULL_DB_NAME = "cgu-nfe.sqlite"
SERIES_DB_NAME = "cgu-nfe-series.sqlite"

SERIES_SCHEMA = """
CREATE TABLE IF NOT EXISTS processamentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month TEXT NOT NULL,
  arquivo_id INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  version TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  counts TEXT,
  detail TEXT,
  run_id TEXT
);
CREATE TABLE IF NOT EXISTS series_uf_ano (
  year INTEGER NOT NULL,
  uf TEXT NOT NULL,
  itens_bruto INTEGER NOT NULL,
  valor_itens_bruto_cents INTEGER NOT NULL,
  itens_cancelados INTEGER NOT NULL,
  valor_itens_cancelados_cents INTEGER NOT NULL,
  notas_bruto INTEGER NOT NULL,
  valor_notas_bruto_cents INTEGER NOT NULL,
  notas_canceladas INTEGER NOT NULL,
  valor_notas_canceladas_cents INTEGER NOT NULL,
  PRIMARY KEY (year, uf)
) WITHOUT ROWID;
"""

MONTH_TABLES = (
    "agg_nota_mun",
    "agg_nota_uf_dest",
    "agg_item",
    "ncm_tipo",
    "auditoria",
    "quarentena",
    "diferencas",
    "reconc_mes",
    "nota_keys",
    "item_keys",
    "duplicidades_meses",
)


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_sqlite(root: Path) -> Path | None:
    """Prefer the slim series file. The 1.7 GB lake stays local. Missing is missing."""
    series = Path(root) / SERIES_DB_NAME
    if series.is_file():
        return series
    full = Path(root) / FULL_DB_NAME
    if full.is_file():
        return full
    return None


def write_series_sqlite(
    path: Path,
    *,
    measures: list[YearUfMeasures],
    months: list[str],
    run_id: str,
    finished_at: str | None,
    version: str = PROCESSING_VERSION,
) -> Path:
    """Write UF × year totals and processing metadata. No keys, names or bronze."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    try:
        conn.executescript(SERIES_SCHEMA)
        started = finished_at or now_iso()
        for month in months:
            conn.execute(
                "INSERT INTO processamentos (month, arquivo_id, sha256, version, started_at, "
                "finished_at, status, run_id) VALUES (?, 0, '', ?, ?, ?, 'CONCLUIDO', ?)",
                (month, version, started, finished_at, run_id),
            )
        conn.executemany(
            "INSERT INTO series_uf_ano (year, uf, itens_bruto, valor_itens_bruto_cents, "
            "itens_cancelados, valor_itens_cancelados_cents, notas_bruto, valor_notas_bruto_cents, "
            "notas_canceladas, valor_notas_canceladas_cents) VALUES (?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    row.year,
                    row.uf,
                    row.itens_bruto,
                    row.valor_itens_bruto_cents,
                    row.itens_cancelados,
                    row.valor_itens_cancelados_cents,
                    row.notas_bruto,
                    row.valor_notas_bruto_cents,
                    row.notas_canceladas,
                    row.valor_notas_canceladas_cents,
                )
                for row in measures
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return path


class Store:
    def __init__(
        self,
        root: Path,
        *,
        run_id: str = "",
        db_path: Path | None = None,
        create_layout: bool = True,
        read_only: bool = False,
    ) -> None:
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.root = Path(root)
        self.bronze = self.root / "bronze"
        self.partial = self.bronze / ".partial"
        self.rejected = self.bronze / ".rejected"
        self.exports = self.root / "exports"
        if create_layout and not read_only:
            for folder in (self.bronze, self.partial, self.rejected, self.exports):
                folder.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path) if db_path is not None else self.root / FULL_DB_NAME
        if read_only:
            uri = f"file:{self.db_path.resolve().as_posix()}?mode=ro"
            self.conn = sqlite3.connect(uri, uri=True, timeout=60, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, timeout=60, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        if self.db_path.name == SERIES_DB_NAME:
            self.conn.executescript(SERIES_SCHEMA)
        else:
            self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except BaseException:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def bronze_path(self, month: str) -> Path:
        return self.bronze / f"{month}_NFe.zip"

    # -- months -----------------------------------------------------------------------------
    def upsert_month(self, month: str, *, url: str, listed: bool | None = None) -> None:
        self.conn.execute(
            "INSERT INTO meses (month, url) VALUES (?, ?) ON CONFLICT(month) DO UPDATE SET url=?",
            (month, url, url),
        )
        if listed is not None:
            self.conn.execute(
                "UPDATE meses SET listed=?, listed_checked_at=? WHERE month=?",
                (int(listed), now_iso(), month),
            )
        self.conn.commit()

    def set_head(self, month: str, status: int | None, size: int | None) -> None:
        self.conn.execute(
            "UPDATE meses SET head_status=?, head_size=?, head_checked_at=? WHERE month=?",
            (status, size, now_iso(), month),
        )
        self.conn.commit()

    def set_blocked(self, month: str, detail: str | None) -> None:
        if detail is None:
            self.conn.execute(
                "UPDATE meses SET blocked=0, blocked_detail=NULL, blocked_at=NULL WHERE month=?",
                (month,),
            )
        else:
            self.conn.execute(
                "UPDATE meses SET blocked=1, blocked_detail=?, blocked_at=? WHERE month=?",
                (detail, now_iso(), month),
            )
        self.conn.commit()

    def set_invalid(self, month: str, detail: str | None) -> None:
        self.conn.execute(
            "UPDATE meses SET invalid=?, invalid_detail=? WHERE month=?",
            (0 if detail is None else 1, detail, month),
        )
        self.conn.commit()

    def month_row(self, month: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM meses WHERE month=?", (month,)).fetchone()

    def month_rows(self) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM meses ORDER BY month"))

    # -- files ------------------------------------------------------------------------------
    def current_file(self, month: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM arquivos WHERE month=? AND status='VALIDATED' ORDER BY id DESC LIMIT 1",
            (month,),
        ).fetchone()

    def register_file(
        self,
        *,
        month: str,
        sha256: str,
        size: int,
        origem: str,
        url_used: str | None,
        original_path: str | None,
        members: list[dict],
        reference_sha256: str | None,
    ) -> int:
        """Record a validated file. A different file for the same month supersedes the old one."""
        existing = self.conn.execute(
            "SELECT id FROM arquivos WHERE month=? AND sha256=?", (month, sha256)
        ).fetchone()
        reference_match = None if reference_sha256 is None else int(reference_sha256 == sha256)
        with self.transaction() as conn:
            conn.execute(
                "UPDATE arquivos SET status='SUPERSEDED' WHERE month=? AND sha256<>?",
                (month, sha256),
            )
            if existing:
                conn.execute(
                    "UPDATE arquivos SET status='VALIDATED', "
                    "reference_sha256=COALESCE(?, reference_sha256), "
                    "reference_match=COALESCE(?, reference_match) WHERE id=?",
                    (reference_sha256, reference_match, existing["id"]),
                )
                return int(existing["id"])
            cursor = conn.execute(
                "INSERT INTO arquivos (month, sha256, size, origem, url_used, original_path, "
                "acquired_at, members, status, reference_sha256, reference_match, run_id) "
                "VALUES (?,?,?,?,?,?,?,?, 'VALIDATED', ?, ?, ?)",
                (
                    month,
                    sha256,
                    size,
                    origem,
                    url_used,
                    original_path,
                    now_iso(),
                    json.dumps(members, ensure_ascii=False),
                    reference_sha256,
                    reference_match,
                    self.run_id,
                ),
            )
            return int(cursor.lastrowid)

    def files(self) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM arquivos ORDER BY month, id"))

    # -- processing -------------------------------------------------------------------------
    def completed_processing(self, month: str, sha256: str, version: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM processamentos WHERE month=? AND sha256=? AND version=? "
            "AND status='CONCLUIDO' ORDER BY id DESC LIMIT 1",
            (month, sha256, version),
        ).fetchone()

    def latest_processing(self, month: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM processamentos WHERE month=? AND status='CONCLUIDO' "
            "ORDER BY id DESC LIMIT 1",
            (month,),
        ).fetchone()

    def start_processing(self, month: str, arquivo_id: int, sha256: str, version: str) -> int:
        cursor = self.conn.execute(
            "INSERT INTO processamentos (month, arquivo_id, sha256, version, started_at, status, "
            "run_id) VALUES (?,?,?,?,?, 'EM_ANDAMENTO', ?)",
            (month, arquivo_id, sha256, version, now_iso(), self.run_id),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def finish_processing(
        self, processing_id: int, status: str, counts: dict | None, detail: str | None
    ) -> None:
        self.conn.execute(
            "UPDATE processamentos SET status=?, finished_at=?, counts=?, detail=? WHERE id=?",
            (status, now_iso(), json.dumps(counts) if counts else None, detail, processing_id),
        )
        self.conn.commit()

    def processed_months(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT month FROM processamentos WHERE status='CONCLUIDO' ORDER BY month"
        )
        return [r["month"] for r in rows]

    def processed_months_for_version(self, version: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT month FROM processamentos WHERE status='CONCLUIDO' AND version=? "
            "ORDER BY month",
            (version,),
        )
        return [r["month"] for r in rows]

    def latest_completed_run(self, version: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM processamentos WHERE status='CONCLUIDO' AND version=? "
            "ORDER BY id DESC LIMIT 1",
            (version,),
        ).fetchone()

    def has_series_table(self) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='series_uf_ano'"
        ).fetchone()
        return row is not None

    def series_year_uf(self) -> list[YearUfMeasures]:
        rows = self.conn.execute(
            "SELECT year, uf, itens_bruto, valor_itens_bruto_cents, itens_cancelados, "
            "valor_itens_cancelados_cents, notas_bruto, valor_notas_bruto_cents, "
            "notas_canceladas, valor_notas_canceladas_cents FROM series_uf_ano "
            "ORDER BY year, uf"
        )
        return [YearUfMeasures(*row) for row in rows]

    def year_uf_item_rows(self, months: list[str]) -> list[tuple[str, str, str, int, int]]:
        return self._year_uf_sum(months, "agg_item", "itens")

    def year_uf_note_rows(self, months: list[str]) -> list[tuple[str, str, str, int, int]]:
        return self._year_uf_sum(months, "agg_nota_mun", "notas")

    def _year_uf_sum(
        self, months: list[str], table: str, count_col: str
    ) -> list[tuple[str, str, str, int, int]]:
        if not months:
            return []
        marks = ",".join("?" * len(months))
        sql = (
            f"SELECT substr(month,1,4), uf, situacao, SUM({count_col}), SUM(valor_cents) "  # noqa: S608
            f"FROM {table} WHERE month IN ({marks}) GROUP BY 1, 2, 3"  # noqa: S608
        )
        return [(r[0], r[1], r[2], int(r[3]), int(r[4])) for r in self.conn.execute(sql, months)]

    # -- bulk -------------------------------------------------------------------------------
    def clear_month(self, conn: sqlite3.Connection, month: str) -> None:
        """Remove what a previous run derived for the month. The manifest is kept."""
        for table in MONTH_TABLES:
            conn.execute(f"DELETE FROM {table} WHERE month=?", (month,))  # noqa: S608

    def insert_many(self, conn: sqlite3.Connection, sql: str, rows: Iterable[tuple]) -> None:
        conn.executemany(sql, rows)
