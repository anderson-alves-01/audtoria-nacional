"""GET /v1/cgu-nfe reads local synthetic aggregates. Never official data."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.cgu_nfe_synthetic import baseline_month
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)
from sirta_api.adapters.ingest.cgu_nfe.acquire import import_zip
from sirta_api.adapters.ingest.cgu_nfe.process import process_month
from sirta_api.adapters.ingest.cgu_nfe.store import Store


def _headers() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _load_baseline(lake: Path) -> None:
    store = Store(lake, run_id="synth-serie")
    figures = baseline_month(lake / "202401_NFe.zip")
    assert import_zip(store, lake / "202401_NFe.zip").accepted
    outcome = process_month(store, "202401")
    assert outcome.status == "CONCLUIDO", outcome.detail
    store.close()
    assert figures["itens"] == 4


def test_cgu_nfe_requires_a_session(api_client) -> None:
    assert api_client.get("/v1/cgu-nfe").status_code == 401


def test_cgu_nfe_is_absent_when_the_sqlite_file_is_missing(api_client, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "sirta_api.application.cgu_nfe_series.cgu_nfe_root", lambda: tmp_path / "missing"
    )
    body = api_client.get("/v1/cgu-nfe", headers=_headers()).json()
    assert body["coverage"] == "AUSENTE"
    assert body["run"] is None
    assert body["items"] == []
    assert body["monthsProcessed"] == 0
    assert len(body["monthsMissing"]) == 60
    assert body["createsTaxCredit"] is False
    assert body["homologated"] is False


def test_cgu_nfe_returns_except_cancelled_item_totals(api_client, monkeypatch, tmp_path) -> None:
    lake = tmp_path / "cgu-nfe"
    _load_baseline(lake)
    monkeypatch.setattr("sirta_api.application.cgu_nfe_series.cgu_nfe_root", lambda: lake)
    response = api_client.get("/v1/cgu-nfe", headers=_headers())
    assert response.status_code == 200
    body = response.json()
    text = response.text
    assert "EMITENTE SINTETICO" not in text
    assert "00000000000000" not in text
    assert body["sourceId"] == "CGU-NFE"
    assert body["valueKind"] == "OBSERVED_DOCUMENT_CENTS"
    assert body["coverage"] == "PARCIAL"
    assert body["monthsProcessed"] == 1
    assert body["run"]["layoutVersion"] == "cgu-nfe-v1"
    assert body["run"] is not None
    by_uf = {item["uf"]: item for item in body["items"]}
    # Baseline: SP has two live items (300.50) and one cancelled (1234.56); MG one live (50.00).
    assert by_uf["SP"]["itens"] == 2
    assert by_uf["SP"]["valorItens"] == "300.50"
    assert by_uf["SP"]["itensCancelados"] == 1
    assert by_uf["MG"]["itens"] == 1
    assert by_uf["MG"]["valorItens"] == "50.00"
    ids = [item["id"] for item in body["reliability"]["indicators"]]
    assert ids == [
        "cgu_nfe_itens_uf_ano",
        "cgu_nfe_valor_itens_uf_ano",
        "simulador_imposto_apurado_dados_publicos",
    ]
    levels = {item["id"]: item["level"] for item in body["reliability"]["indicators"]}
    assert levels["cgu_nfe_itens_uf_ano"] == "CONFERIDO"
    assert levels["cgu_nfe_valor_itens_uf_ano"] == "CONFERIDO"
    assert levels["simulador_imposto_apurado_dados_publicos"] == "NAO_CONFIAVEL"


def test_cgu_nfe_filters_uf_and_rejects_unknown(api_client, monkeypatch, tmp_path) -> None:
    lake = tmp_path / "cgu-nfe"
    _load_baseline(lake)
    monkeypatch.setattr("sirta_api.application.cgu_nfe_series.cgu_nfe_root", lambda: lake)
    body = api_client.get("/v1/cgu-nfe?uf=SP", headers=_headers()).json()
    assert {item["uf"] for item in body["items"]} == {"SP"}
    assert api_client.get("/v1/cgu-nfe?uf=XX", headers=_headers()).status_code == 422
    assert api_client.get("/v1/cgu-nfe?ano=2019", headers=_headers()).status_code == 422
