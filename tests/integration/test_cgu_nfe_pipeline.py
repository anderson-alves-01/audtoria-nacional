"""End to end CGU NF-e pipeline: import, process, audit, export.

All ZIPs here are SYNTHETIC (see ``tests/helpers/cgu_nfe_synthetic.py``). They exercise the rules
and never stand for official data. Real data is not touched by any test.
"""

import csv
import json
import sqlite3
import zipfile
from pathlib import Path

import pytest
from tests.helpers.cgu_nfe_synthetic import (
    ITEM_HEADER,
    NOTE_HEADER,
    access_key,
    baseline_month,
    build_zip,
    event_row,
    item_row,
    note_row,
)

from sirta_api.adapters.ingest.cgu_nfe import __main__ as cli
from sirta_api.adapters.ingest.cgu_nfe import export as export_mod
from sirta_api.adapters.ingest.cgu_nfe.acquire import import_zip
from sirta_api.adapters.ingest.cgu_nfe.export import Exporter, ExportError
from sirta_api.adapters.ingest.cgu_nfe.inventory import month_statuses
from sirta_api.adapters.ingest.cgu_nfe.process import process_month
from sirta_api.adapters.ingest.cgu_nfe.reference import load_reference, reconcile_reference
from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.adapters.ingest.cgu_nfe.xlsx import read_xlsx
from sirta_api.domain import cgu_nfe as d

REFERENCE_PACKAGE = Path("docs/data/CGU_2021_2025_Detalhamento_PARCIAL.zip")


@pytest.fixture
def store(tmp_path: Path):
    s = Store(tmp_path / "lake", run_id="itest")
    yield s
    s.close()


def ingest(store: Store, tmp: Path, month: str, notes, items, events=None, **kwargs):
    path = tmp / f"{month}_NFe.zip"
    build_zip(path, month, notes, items, events, **kwargs)
    imported = import_zip(store, path, month=month)
    assert imported.accepted, imported.detail
    return process_month(store, month)


def baseline(store: Store, tmp: Path, month: str = "202401"):
    figures = baseline_month(tmp / f"{month}_NFe.zip")
    assert import_zip(store, tmp / f"{month}_NFe.zip").accepted
    return process_month(store, month), figures


def q(store: Store, sql: str, *params):
    return [tuple(r) for r in store.conn.execute(sql, params)]


def audit(store: Store, month: str) -> dict[str, tuple]:
    return {
        r[0]: (r[1], r[2])
        for r in q(
            store, "SELECT check_id, resultado, quantidade FROM auditoria WHERE month=?", month
        )
    }


def snapshot(store: Store, month: str) -> dict[str, list]:
    tables = ("agg_nota_mun", "agg_nota_uf_dest", "agg_item", "nota_keys", "item_keys")
    return {
        t: sorted(q(store, f"SELECT * FROM {t} WHERE month=?", month), key=repr) for t in tables
    }


# -- reading and aggregation -------------------------------------------------------------------
def test_baseline_totals_reconcile_with_the_source(store: Store, tmp_path: Path) -> None:
    outcome, figures = baseline(store, tmp_path)
    assert outcome.status == "CONCLUIDO"
    c = outcome.counts
    assert (c["notas_lidas"], c["notas_aceitas"]) == (3, 3)
    assert (c["itens_lidos"], c["itens_aceitos"]) == (4, 4)
    assert c["valor_notas_centavos"] == figures["valor_notas"]
    assert c["valor_itens_centavos"] == figures["valor_itens"]
    assert c["quarentena"] == 0
    results = audit(store, "202401")
    assert results["RECONCILIACAO_NOTAS_UF_MUNICIPIO"][0] == "OK"
    assert results["RECONCILIACAO_NOTAS_UF_DESTINO"][0] == "OK"
    assert results["RECONCILIACAO_ITENS"][0] == "OK"


def test_municipality_spelling_and_identifiers_are_preserved(store: Store, tmp_path: Path) -> None:
    baseline(store, tmp_path)
    cities = {r[0] for r in q(store, "SELECT DISTINCT municipio FROM agg_nota_mun")}
    assert cities == {"MUNICÍPIO SINTÉTICO A", "MUNICÍPIO SINTÉTICO B"}  # cp1252 accents kept
    ncms = {r[0] for r in q(store, "SELECT DISTINCT ncm FROM agg_item")}
    assert ncms == {"01012100", "02011000"}  # leading zero kept: text, not a number
    quantity = q(
        store,
        "SELECT quantidade FROM agg_item WHERE ncm='01012100' AND uf='SP' "
        "AND situacao='SEM_EVENTO_INFORMADO'",
    )
    assert quantity == [("2.5000",)]  # source precision, not 2.5


def test_issuer_location_and_destination_are_separate_dimensions(store, tmp_path) -> None:
    baseline(store, tmp_path)
    by_city = q(store, "SELECT uf, municipio FROM agg_nota_mun ORDER BY 1,2")
    by_dest = q(store, "SELECT uf, uf_dest FROM agg_nota_uf_dest ORDER BY 1,2")
    assert ("MG", "MUNICÍPIO SINTÉTICO B") in by_city
    assert ("SP", "RJ") in by_dest and ("MG", "MG") in by_dest
    assert all("RJ" not in r for r in by_city)  # destination never leaks into the supplier city


def test_cancellation_rule_and_raw_scope(store: Store, tmp_path: Path) -> None:
    outcome, figures = baseline(store, tmp_path)
    cancelled = q(
        store, "SELECT SUM(notas), SUM(valor_cents) FROM agg_nota_mun WHERE situacao='CANCELADA'"
    )
    assert cancelled == [(1, 123456)]
    total = q(store, "SELECT SUM(notas), SUM(valor_cents) FROM agg_nota_mun")
    assert total == [(3, figures["valor_notas"])]  # raw scope keeps the cancelled note
    assert audit(store, "202401")["NOTAS_CANCELADAS_PELOS_EVENTOS"][1] == 1


def test_event_table_alone_can_cancel_a_note(store: Store, tmp_path: Path) -> None:
    key = access_key(1)
    notes = [note_row(1, event="Ciência da Operação")]
    items = [item_row(key)]
    events = [event_row(key, "Cancelamento de NF-e homologado"), event_row(access_key(99), "x")]
    ingest(store, tmp_path, "202401", notes, items, events)
    assert q(store, "SELECT situacao FROM agg_nota_mun") == [("CANCELADA",)]
    assert audit(store, "202401")["EVENTOS_SEM_NOTA"] == ("INFO", 1)


def test_note_without_any_event_is_not_called_authorized(store: Store, tmp_path: Path) -> None:
    ingest(store, tmp_path, "202401", [note_row(1)], [item_row(access_key(1))], [])
    assert q(store, "SELECT situacao FROM agg_nota_mun") == [("SEM_EVENTO_INFORMADO",)]


# -- idempotency and versions ------------------------------------------------------------------
def test_rerun_is_idempotent_and_forced_rerun_gives_the_same_result(store, tmp_path) -> None:
    baseline(store, tmp_path)
    before = snapshot(store, "202401")
    again = process_month(store, "202401")
    assert again.status == "JA_PROCESSADO"
    assert snapshot(store, "202401") == before
    forced = process_month(store, "202401", force=True)
    assert forced.status == "CONCLUIDO"
    assert snapshot(store, "202401") == before
    assert len(q(store, "SELECT 1 FROM nota_keys")) == 3  # keys are not duplicated
    runs = q(store, "SELECT status FROM processamentos WHERE month='202401' ORDER BY id")
    assert runs == [("CONCLUIDO",), ("CONCLUIDO",)]


def test_new_processing_version_reprocesses_and_a_new_file_replaces_the_month(store, tmp_path):
    baseline(store, tmp_path)
    assert process_month(store, "202401", version="cgu-nfe-v2").status == "CONCLUIDO"
    replacement = tmp_path / "second" / "202401_NFe.zip"
    replacement.parent.mkdir()
    build_zip(
        replacement,
        "202401",
        [note_row(5, value="10,00")],
        [item_row(access_key(5), value="10,00")],
    )
    assert import_zip(store, replacement).accepted
    assert process_month(store, "202401").status == "CONCLUIDO"
    assert q(store, "SELECT SUM(notas), SUM(valor_cents) FROM agg_nota_mun") == [(1, 1000)]
    assert len(q(store, "SELECT 1 FROM nota_keys")) == 1
    assert [r[0] for r in q(store, "SELECT status FROM arquivos ORDER BY id")] == [
        "SUPERSEDED",
        "VALIDATED",
    ]  # the manifest keeps the history


# -- duplicates, orphans, dates ----------------------------------------------------------------
def test_identical_repeats_count_once_and_are_reported(store: Store, tmp_path: Path) -> None:
    key = access_key(1)
    notes = [note_row(1), note_row(1)]
    items = [item_row(key, "1"), item_row(key, "1")]
    outcome = ingest(store, tmp_path, "202401", notes, items, [])
    assert (outcome.counts["notas_lidas"], outcome.counts["notas_aceitas"]) == (2, 1)
    assert (outcome.counts["itens_lidos"], outcome.counts["itens_aceitos"]) == (2, 1)
    results = audit(store, "202401")
    assert results["CHAVE_NOTA_DUPLICADA_IDENTICA"] == ("INFO", 1)
    assert results["ITEM_DUPLICADO_IDENTICO"] == ("INFO", 1)


def test_conflicting_duplicate_note_is_quarantined_not_picked(store: Store, tmp_path: Path) -> None:
    key = access_key(1)
    notes = [note_row(1, value="100,00"), note_row(1, value="999,00"), note_row(2, value="5,00")]
    items = [item_row(key, "1", value="100,00"), item_row(access_key(2), "1", value="5,00")]
    outcome = ingest(store, tmp_path, "202401", notes, items, [])
    assert outcome.counts["notas_aceitas"] == 1  # neither version of the conflicting key
    assert q(store, "SELECT SUM(valor_cents) FROM agg_nota_mun") == [(500,)]
    reasons = q(store, "SELECT motivo, COUNT(*) FROM quarentena GROUP BY motivo")
    assert reasons == [("CHAVE_DUPLICADA_CONFLITANTE", 2)]
    lines = q(store, "SELECT linha FROM quarentena ORDER BY linha")
    assert lines == [(2,), (3,)]  # both copies, by file line, for review
    assert audit(store, "202401")["CHAVE_NOTA_DUPLICADA_CONFLITANTE"] == ("ALERTA", 1)
    assert q(store, "SELECT situacao, itens FROM agg_item WHERE ncm='01012100' ORDER BY 1") == [
        ("NOTA_EM_QUARENTENA", 1),
        ("SEM_EVENTO_INFORMADO", 1),
    ]


def test_conflicting_duplicate_item_leaves_no_version_in_the_totals(store, tmp_path) -> None:
    key = access_key(1)
    items = [
        item_row(key, "1", value="60,00"),
        item_row(key, "1", value="70,00"),
        item_row(key, "2", value="30,00"),
    ]
    outcome = ingest(store, tmp_path, "202401", [note_row(1, value="100,00")], items, [])
    assert outcome.counts["itens_aceitos"] == 1
    assert q(store, "SELECT SUM(valor_cents), SUM(itens) FROM agg_item") == [(3000, 1)]
    assert audit(store, "202401")["ITEM_DUPLICADO_CONFLITANTE"] == ("ALERTA", 1)
    diff = q(store, "SELECT valor_nota_cents, soma_itens_cents, diferenca_cents FROM diferencas")
    assert diff == [(10000, 3000, 7000)]  # recorded, not forced to match


def test_items_without_a_note_are_reported_and_kept_apart(store: Store, tmp_path: Path) -> None:
    orphan = access_key(77)
    outcome = ingest(
        store,
        tmp_path,
        "202401",
        [note_row(1)],
        [item_row(access_key(1)), item_row(orphan, "1")],
        [],
    )
    assert outcome.counts["itens_aceitos"] == 2
    assert q(store, "SELECT itens FROM agg_item WHERE situacao='ITEM_SEM_NOTA'") == [(1,)]
    assert audit(store, "202401")["ITENS_SEM_NOTA"] == ("ALERTA", 1)


def test_dates_outside_the_month_are_reported_and_kept(store: Store, tmp_path: Path) -> None:
    notes = [note_row(1), note_row(2, day="05")]
    notes[1][5] = "05/12/2023"
    items = [item_row(access_key(1)), item_row(access_key(2))]
    items[1][5] = "05/12/2023"
    ingest(store, tmp_path, "202401", notes, items, [])
    results = audit(store, "202401")
    assert results["NOTA_DATA_FORA_DO_MES"] == ("ALERTA", 1)
    assert results["ITEM_DATA_FORA_DO_MES"] == ("ALERTA", 1)
    assert q(store, "SELECT SUM(notas) FROM agg_nota_mun") == [(2,)]


def test_data_that_does_not_belong_to_the_month_is_refused_before_storing(store, tmp_path):
    path = tmp_path / "202401_NFe.zip"
    build_zip(
        path,
        "202402",
        [note_row(1, "202402")],
        [item_row(access_key(1, "202402"), month="202402")],
        [],
    )
    assert import_zip(store, path, month="202401").accepted
    outcome = process_month(store, "202401")
    assert outcome.status == "ERRO"
    assert "não pertencem ao mês" in outcome.detail
    assert q(store, "SELECT COUNT(*) FROM agg_nota_mun") == [(0,)]
    assert store.month_row("202401")["invalid"] == 1
    state = {s.month: s for s in month_statuses(store)}["202401"]
    assert state.state == d.STATE_INVALID or state.state == d.STATE_VALIDATED


# -- numbers, blanks, schema -------------------------------------------------------------------
def test_blank_values_are_never_zero_and_inexact_values_are_quarantined(store, tmp_path) -> None:
    key1, key2, key3 = (access_key(n) for n in (1, 2, 3))
    notes = [note_row(1, value=""), note_row(2, value="10,005"), note_row(3, value="20,00")]
    items = [
        item_row(key1, "1", value="", quantity=""),
        item_row(key3, "1", value="20,00", quantity="1,5"),
        item_row(key3, "2", value="1,234", quantity="1"),
        item_row(key3, "3", value="1,00", quantity="x"),
    ]
    outcome = ingest(store, tmp_path, "202401", notes, items, [])
    assert outcome.counts["notas_aceitas"] == 2  # the 10,005 note is quarantined, never rounded
    reasons = dict(q(store, "SELECT motivo, COUNT(*) FROM quarentena GROUP BY motivo"))
    assert reasons == {
        "VALOR_NOTA_INVALIDO": 1,
        "VALOR_ITEM_INVALIDO": 1,
        "QUANTIDADE_INVALIDA": 1,
    }
    assert q(store, "SELECT SUM(notas_sem_valor), SUM(valor_cents) FROM agg_nota_mun") == [
        (1, 2000)
    ]
    blank = q(
        store,
        "SELECT itens_sem_quantidade, itens_sem_valor, quantidade, valor_cents "
        "FROM agg_item WHERE ncm='01012100' AND situacao='SEM_EVENTO_INFORMADO' "
        "ORDER BY quantidade",
    )
    assert blank[0][:2] == (1, 1)  # counted as missing, not as zero
    results = audit(store, "202401")
    assert results["NOTA_VALOR_AUSENTE"] == ("ALERTA", 1)
    assert results["ITEM_VALOR_AUSENTE"] == ("ALERTA", 1)
    assert results["ITEM_QUANTIDADE_AUSENTE"] == ("ALERTA", 1)


def test_missing_required_column_fails_closed(store: Store, tmp_path: Path) -> None:
    header = [h for h in ITEM_HEADER if h != "CFOP"]
    path = tmp_path / "202401_NFe.zip"
    build_zip(path, "202401", [note_row(1)], [], [], item_header=header)
    assert import_zip(store, path).accepted
    outcome = process_month(store, "202401")
    assert outcome.status == "ERRO"
    assert "cfop" in outcome.detail
    assert q(store, "SELECT COUNT(*) FROM agg_nota_mun") == [(0,)]
    assert store.current_file("202401") is not None  # the ZIP stays; only the month is refused
    assert q(store, "SELECT status FROM processamentos") == [("ERRO",)]


def test_extra_columns_are_reported_not_dropped_silently(store: Store, tmp_path: Path) -> None:
    header = [*NOTE_HEADER, "COLUNA NOVA SINTETICA"]
    notes = [[*note_row(1), "x"]]
    ingest(store, tmp_path, "202401", notes, [item_row(access_key(1))], [], note_header=header)
    found = q(
        store, "SELECT detalhe FROM auditoria WHERE check_id LIKE 'COLUNAS_NAO_MAPEADAS_NOTA%'"
    )
    assert "COLUNA NOVA SINTETICA" in found[0][0]


def test_utf8_with_bom_and_other_delimiter_are_detected_and_reported(store, tmp_path) -> None:
    notes = [note_row(1, city="SÃO SINTÉTICO")]
    ingest(
        store,
        tmp_path,
        "202401",
        notes,
        [item_row(access_key(1), city="SÃO SINTÉTICO")],
        [],
        encoding="utf-8-sig",
        delimiter=",",
    )
    assert q(store, "SELECT municipio FROM agg_nota_mun") == [("SÃO SINTÉTICO",)]
    formats = q(store, "SELECT resultado FROM auditoria WHERE check_id LIKE 'FORMATO_NOTA%'")
    assert formats == [("ALERTA",)]  # not the documented ';' delimiter: reported


def test_cross_month_repeated_key_is_reported_and_kept_in_both(store, tmp_path) -> None:
    key = access_key(1)
    ingest(store, tmp_path, "202401", [note_row(1)], [item_row(key)], [])
    ingest(
        store,
        tmp_path,
        "202402",
        [note_row(1, "202402", key=key)],
        [item_row(key, month="202402")],
        [],
    )
    results = audit(store, "202402")
    assert results["CHAVE_NOTA_TAMBEM_EM_202401"][1] == 1
    assert results["CHAVE_ITEM_TAMBEM_EM_202401"][1] == 1
    assert q(store, "SELECT SUM(notas) FROM agg_nota_mun") == [(2,)]


def test_blocked_and_invalid_months_are_not_processed(store: Store, tmp_path: Path) -> None:
    assert process_month(store, "202402").status == "ERRO"
    bad = tmp_path / "202402_NFe.zip"
    bad.write_bytes(b"<html>Human Verification</html>")
    assert not import_zip(store, bad).accepted
    assert process_month(store, "202402").status == "ERRO"
    assert q(store, "SELECT COUNT(*) FROM agg_nota_mun") == [(0,)]


def test_store_keeps_no_personal_identifiers(store: Store, tmp_path: Path) -> None:
    baseline(store, tmp_path)
    store.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    blob = store.db_path.read_bytes()
    assert b"EMITENTE SINTETICO" not in blob
    assert b"00000000000000" not in blob
    assert access_key(1).encode() not in blob  # only digests of keys are stored


# -- export ------------------------------------------------------------------------------------
def test_export_is_partial_with_six_sheets_and_a_sixty_month_series(store, tmp_path) -> None:
    baseline(store, tmp_path)
    zero_month = ingest(store, tmp_path, "202402", [], [], [])
    assert zero_month.status == "CONCLUIDO"  # processed and genuinely empty
    report = Exporter(store, prefix="SINTETICO_TESTE").run(tmp_path / "out")
    assert report.partial and report.ok
    assert "PARCIAL" in report.workbook.path.name
    assert all("PARCIAL" in f.path.name for f in report.csv_files)

    sheets = read_xlsx(report.workbook.path)
    assert list(sheets) == [
        "Consolidado por UF",
        "Municípios",
        "Bens e serviços",
        "Série histórica",
        "Auditoria",
        "Fontes e metodologia",
    ]
    series = sheets["Série histórica"]
    start = next(i for i, r in enumerate(series) if r[:1] == ["Mês (AAAAMM)"])
    rows = {r[0]: r for r in series[start + 1 :]}
    assert len(rows) == 60
    header = series[start]
    notes_col = header.index("Notas (bruto)")
    assert rows["202401"][notes_col] == "3"
    assert rows["202402"][notes_col] == "0"  # real zero
    assert rows["202403"][notes_col] == "SEM DADOS"  # absence is not zero
    assert rows["202101"][header.index("Cobertura")] == "SEM DADOS"
    assert "não listado" in rows["202101"][header.index("Motivo da ausência")]
    assert any(
        "COBERTURA PARCIAL" in cell for row in sheets["Consolidado por UF"][:4] for cell in row
    )


def test_export_separates_raw_cancelled_and_filtered_views(store: Store, tmp_path: Path) -> None:
    baseline(store, tmp_path)
    report = Exporter(store, prefix="SINTETICO_TESTE").run(tmp_path / "out")
    uf = next(f for f in report.csv_files if f.name == "por_uf")
    with uf.path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    sp = next(r for r in rows if r["UF do emitente (origem do fornecedor)"] == "SP")
    assert sp["Notas (bruto, inclui canceladas)"] == "2"
    assert sp["Valor das notas (R$, bruto)"] == "1535,06"  # exact, decimal comma
    assert sp["Notas canceladas (eventos)"] == "1"
    assert sp["Valor das notas canceladas (R$)"] == "1234,56"
    assert sp["Notas exceto canceladas"] == "1"
    assert sp["Valor das notas exceto canceladas (R$)"] == "300,50"
    assert sp["Meses com dados no ano"] == "1"


def test_exports_hold_no_names_documents_or_full_keys(store: Store, tmp_path: Path) -> None:
    key = access_key(1)
    notes = [note_row(1, value="1,00"), note_row(1, value="2,00")]  # conflicting: quarantine
    ingest(store, tmp_path, "202401", notes, [item_row(key)], [])
    report = Exporter(store, prefix="SINTETICO_TESTE").run(tmp_path / "out")
    quarantine = next(f for f in report.csv_files if f.name == "quarentena")
    assert quarantine.rows == 2
    files = [f.path for f in report.csv_files] + [report.workbook.path]
    for path in files:
        data = path.read_bytes()
        if path.suffix == ".xlsx":
            with zipfile.ZipFile(path) as archive:
                data = b"".join(archive.read(n) for n in archive.namelist())
        assert b"EMITENTE SINTETICO" not in data
        assert b"00000000000000" not in data
        assert key.encode() not in data


def test_export_without_processed_months_is_refused(store: Store) -> None:
    with pytest.raises(ExportError, match="nenhum mês processado"):
        Exporter(store).run()


def test_excel_row_limit_falls_back_to_a_coarser_sheet_and_a_complete_csv(
    store, tmp_path, monkeypatch
):
    baseline(store, tmp_path)
    monkeypatch.setattr(export_mod, "GRAIN_ROW_LIMIT", 1)
    report = Exporter(store, prefix="SINTETICO_TESTE").run(tmp_path / "out")
    assert "CFOP omitido" in report.sheet_grain_note
    full = next(f for f in report.csv_files if f.name == "bens_servicos_completo")
    with full.path.open(encoding="utf-8-sig", newline="") as handle:
        full_rows = list(csv.DictReader(handle, delimiter=";"))
    assert {r["CFOP (código da fonte, texto)"] for r in full_rows} == {"5102"}
    assert sum(int(r["Itens (bruto)"]) for r in full_rows) == 4
    goods = read_xlsx(report.workbook.path)["Bens e serviços"]
    header = next(r for r in goods if r[:1] == ["Ano"])
    body = goods[goods.index(header) + 1 :]
    assert sum(int(r[header.index("Itens (bruto)")]) for r in body) == 4  # nothing dropped
    assert all(r[header.index("CFOP (código da fonte, texto)")].startswith("(não") for r in body)


def test_quantities_are_not_summed_across_units(store: Store, tmp_path: Path) -> None:
    baseline(store, tmp_path)
    report = Exporter(store, prefix="SINTETICO_TESTE").run(tmp_path / "out")
    full = next(f for f in report.csv_files if f.name == "bens_servicos_completo")
    with full.path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    qty_header = "Quantidade comercial declarada (bruto; só soma a mesma unidade)"
    got = {
        (
            r["UF do emitente"],
            r["NCM (código da fonte, texto)"],
            r["Unidade comercial declarada"],
        ): r[qty_header]
        for r in rows
    }
    assert got == {
        ("MG", "01012100", "UN"): "1,0000",
        ("SP", "01012100", "UN"): "5,5000",  # 2,5 + 3 of the same NCM and unit
        ("SP", "02011000", "KG"): "1,0000",  # a different unit is a different row
    }


def test_sixty_months_processed_drops_the_partial_label(store: Store, tmp_path: Path) -> None:
    for month in d.requested_months():
        key = access_key(1, month)
        ingest(
            store, tmp_path, month, [note_row(1, month, key=key)], [item_row(key, month=month)], []
        )
    report = Exporter(store, prefix="SINTETICO_TESTE").run(tmp_path / "out")
    assert not report.partial and report.ok
    assert report.workbook.path.name == "SINTETICO_TESTE_COMPLETO.xlsx"
    assert not report.months_pending
    assert q(store, "SELECT COUNT(DISTINCT month) FROM nota_keys") == [(60,)]


# -- CLI ---------------------------------------------------------------------------------------
def test_cli_import_process_audit_export_and_status(tmp_path: Path, capsys) -> None:
    root = str(tmp_path / "lake")
    zip_path = tmp_path / "202401_NFe.zip"
    baseline_month(zip_path)
    assert cli.main(["import-zip", str(zip_path), "--root", root]) == 0
    assert cli.main(["process", "--root", root]) == 0
    assert cli.main(["process", "--root", root]) == 0  # idempotent
    assert "JA_PROCESSADO" in capsys.readouterr().out
    assert cli.main(["audit", "--root", root]) == 0
    out_dir = str(tmp_path / "out")
    assert (
        cli.main(["export", "--root", root, "--prefix", "SINTETICO_TESTE", "--out-dir", out_dir])
        == 0
    )
    assert (tmp_path / "out" / "SINTETICO_TESTE_PARCIAL.xlsx").is_file()
    assert cli.main(["status", "--root", root, "--months", "202401", "202402"]) == 0
    status = capsys.readouterr().out
    assert "PROCESSAMENTO_CONCLUIDO" in status


def test_cli_export_series_writes_uf_year_sqlite_without_keys(tmp_path: Path) -> None:
    root = str(tmp_path / "lake")
    zip_path = tmp_path / "202401_NFe.zip"
    baseline_month(zip_path)
    assert cli.main(["import-zip", str(zip_path), "--root", root]) == 0
    assert cli.main(["process", "--root", root]) == 0
    out = tmp_path / "cgu-nfe-series.sqlite"
    assert cli.main(["export-series", "--root", root, "--out", str(out)]) == 0
    assert out.is_file()
    conn = sqlite3.connect(out)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"processamentos", "series_uf_ano"} <= tables
    assert tables <= {"processamentos", "series_uf_ano", "sqlite_sequence"}
    schema = " ".join(row[0] for row in conn.execute("SELECT sql FROM sqlite_master")).lower()
    assert "chave" not in schema
    months = [row[0] for row in conn.execute("SELECT month FROM processamentos ORDER BY month")]
    assert months == ["202401"]
    conn.close()


def test_cli_export_with_nothing_processed_and_bad_months(tmp_path: Path) -> None:
    root = str(tmp_path / "lake")
    assert cli.main(["export", "--root", root]) == 2
    with pytest.raises(SystemExit):
        cli.main(["status", "--root", root, "--months", "2024-01"])
    zip_path = tmp_path / "download.zip"
    baseline_month(zip_path)
    assert cli.main(["import-zip", str(zip_path), "--root", root]) == 1  # month cannot be inferred


# -- reference ---------------------------------------------------------------------------------
def _reference_zip(path: Path, rows: list[tuple[str, int, int, str]]) -> Path:
    header = (
        "Mês;Notas lidas;Itens lidos;Chaves duplicadas;Itens duplicados;Itens sem nota;"
        "Itens fora do mês;Integridade estrutural;SHA-256 do ZIP;URL oficial\n"
    )
    body = "".join(f"{m};{n};{i};0;0;0;0;OK;{sha};{d.month_url(m)}\n" for m, n, i, sha in rows)
    detail = (
        "Ano;UF emitente;NCM;Tipo NCM;CFOP;Unidade declarada;Itens;Quantidade declarada;"
        "Valor itens R$\n"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Manifesto_auditoria.csv", ("\ufeff" + header + body).encode("utf-8"))
        archive.writestr("CGU_2021_2025_NCM_CFOP_UF_Unidade.csv", detail.encode("utf-8"))
    return path


def test_reference_reconciliation_only_claims_what_it_can_prove(store, tmp_path) -> None:
    baseline(store, tmp_path)
    sha = store.current_file("202401")["sha256"]
    ok = reconcile_reference(
        store,
        load_reference(
            _reference_zip(
                tmp_path / "ref_ok.zip", [("202401", 3, 4, sha), ("202402", 10, 10, "a" * 64)]
            )
        ),
    )
    verdicts = {r.month: r.verdict for r in ok.rows}
    assert verdicts["202401"] == "REPRODUZIDO"
    assert verdicts["202402"] == "SEM_ZIP_LOCAL"
    assert verdicts["202101"] == "SEM_REFERENCIA"
    assert not ok.reproduced  # one of two reference months only

    other = reconcile_reference(
        store,
        load_reference(_reference_zip(tmp_path / "ref_other.zip", [("202401", 3, 4, "b" * 64)])),
    )
    assert {r.month: r.verdict for r in other.rows}["202401"] == "ARQUIVO_DIFERENTE_NAO_COMPARAVEL"

    counts = reconcile_reference(
        store, load_reference(_reference_zip(tmp_path / "ref_counts.zip", [("202401", 9, 9, sha)]))
    )
    assert {r.month: r.verdict for r in counts.rows}["202401"] == "CONTAGEM_DIVERGENTE"


def test_reference_reconciliation_without_local_files_states_the_limit(store, tmp_path) -> None:
    reference = load_reference(_reference_zip(tmp_path / "ref.zip", [("202401", 3, 4, "c" * 64)]))
    report = reconcile_reference(store, reference)
    assert not report.reproduced
    assert any("NÃO foram reproduzidos" in line for line in report.summary)
    assert {r.verdict for r in report.rows} <= {"SEM_ZIP_LOCAL", "SEM_REFERENCIA"}


@pytest.mark.skipif(not REFERENCE_PACKAGE.is_file(), reason="reference package not in checkout")
def test_earlier_package_is_internally_consistent() -> None:
    reference = load_reference(REFERENCE_PACKAGE)
    assert reference.notes_total == 3_878_534
    assert reference.items_total == 13_482_862
    assert reference.detail_items == 13_482_862
    assert reference.detail_rows == 969_885
    assert reference.detail_value_cents == 19_684_509_216_869
    assert len(reference.months) == 30
    assert json.dumps(sorted(reference.months))[:9] == '["202104"'
