"""Slim CGU series SQLite: UF × year totals, no keys, no bronze."""

from __future__ import annotations

import sqlite3

from sirta_api.adapters.ingest.cgu_nfe.store import (
    FULL_DB_NAME,
    SERIES_DB_NAME,
    Store,
    resolve_sqlite,
    write_series_sqlite,
)
from sirta_api.domain.cgu_nfe import YearUfMeasures


def test_resolve_sqlite_prefers_series_then_full_then_none(tmp_path) -> None:
    assert resolve_sqlite(tmp_path / "missing") is None
    (tmp_path / FULL_DB_NAME).write_bytes(b"full")
    assert resolve_sqlite(tmp_path) == tmp_path / FULL_DB_NAME
    (tmp_path / SERIES_DB_NAME).write_bytes(b"slim")
    assert resolve_sqlite(tmp_path) == tmp_path / SERIES_DB_NAME


def test_write_series_sqlite_round_trip_without_keys(tmp_path) -> None:
    path = tmp_path / SERIES_DB_NAME
    measure = YearUfMeasures(
        year=2024,
        uf="SP",
        itens_bruto=12,
        valor_itens_bruto_cents=1200,
        itens_cancelados=2,
        valor_itens_cancelados_cents=200,
        notas_bruto=3,
        valor_notas_bruto_cents=900,
        notas_canceladas=1,
        valor_notas_canceladas_cents=100,
    )
    write_series_sqlite(
        path,
        measures=[measure],
        months=["202401", "202402"],
        run_id="run-unit",
        finished_at="2026-10-29T12:00:00Z",
    )
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"processamentos", "series_uf_ano"} <= tables
    assert tables <= {"processamentos", "series_uf_ano", "sqlite_sequence"}
    column_blob = " ".join(
        row[1] for row in conn.execute("SELECT name, sql FROM sqlite_master")
    ).lower()
    assert "chave" not in column_blob
    assert "cpf" not in column_blob
    assert "cnpj" not in column_blob
    months = [
        row["month"]
        for row in conn.execute(
            "SELECT month FROM processamentos WHERE status='CONCLUIDO' ORDER BY month"
        )
    ]
    assert months == ["202401", "202402"]
    row = conn.execute("SELECT * FROM series_uf_ano").fetchone()
    loaded = YearUfMeasures(
        year=row["year"],
        uf=row["uf"],
        itens_bruto=row["itens_bruto"],
        valor_itens_bruto_cents=row["valor_itens_bruto_cents"],
        itens_cancelados=row["itens_cancelados"],
        valor_itens_cancelados_cents=row["valor_itens_cancelados_cents"],
        notas_bruto=row["notas_bruto"],
        valor_notas_bruto_cents=row["valor_notas_bruto_cents"],
        notas_canceladas=row["notas_canceladas"],
        valor_notas_canceladas_cents=row["valor_notas_canceladas_cents"],
    )
    assert loaded == measure
    assert loaded.itens == 10
    assert loaded.valor_itens_cents == 1000
    conn.close()
    store = Store(tmp_path, db_path=path, create_layout=False, read_only=True)
    try:
        assert store.has_series_table()
        assert store.processed_months_for_version("cgu-nfe-v1") == ["202401", "202402"]
        assert store.series_year_uf() == [measure]
        assert store.latest_completed_run("cgu-nfe-v1")["run_id"] == "run-unit"
    finally:
        store.close()
