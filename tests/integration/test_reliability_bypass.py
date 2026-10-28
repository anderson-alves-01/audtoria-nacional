"""Nenhum consumidor consegue contornar a política de confiabilidade dos indicadores."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.models import AuditEvent
from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)
from sirta_api.application import indicator_reliability as application
from sirta_api.domain.indicator_reliability import parse_registry

FISCAL_USE = "/v1/indicator-reliability/{}/fiscal-use"


def _lenient(api_client) -> TestClient:
    """Mesmo app e mesmas sobreposições, mas devolve a resposta 500 em vez de relançar o erro."""
    return TestClient(api_client.app, raise_server_exceptions=False)


def _headers() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


@pytest.mark.parametrize(
    "indicator_id",
    [
        "SPED_COMPRAS_UF",
        "sped_compras_uf%20",
        "%20sped_compras_uf",
        "sped_compras_uf%00",
        "sped_compras_uf;CONFERIDO",
        "sped_compras_uf%2F..%2Ficms_aliquota_ac",
        "..%2F..%2Fconfig%2Findicator-reliability.yaml",
        "CONFERIDO",
        "*",
    ],
)
def test_lookalike_ids_never_authorize_fiscal_use(api_client, indicator_id) -> None:
    response = api_client.get(FISCAL_USE.format(indicator_id), headers=_headers())
    assert response.status_code in (404, 409)
    assert "usableForFiscalCalculation" not in response.text


@pytest.mark.parametrize(
    ("query", "headers"),
    [
        ("?level=CONFERIDO", {}),
        ("?conferred=true&force=1", {}),
        ("", {"X-Reliability-Level": "CONFERIDO"}),
        ("", {"X-Override": "1", "X-Conferido": "true"}),
    ],
)
def test_the_caller_cannot_force_the_level(api_client, query, headers) -> None:
    response = api_client.get(
        FISCAL_USE.format("sped_compras_uf") + query, headers={**_headers(), **headers}
    )
    assert response.status_code == 409


def test_every_shipped_indicator_is_refused_for_fiscal_use(api_client) -> None:
    registry = application.load_registry()
    assert registry
    for indicator_id in registry:
        response = api_client.get(FISCAL_USE.format(indicator_id), headers=_headers())
        assert response.status_code == 409, indicator_id


def test_only_a_fully_evidenced_conferido_can_be_used_and_the_use_is_audited(
    api_client, db_session, monkeypatch
) -> None:
    registry = parse_registry(
        {
            "indicators": [
                {
                    "id": "indicador_sintetico",
                    "level": "CONFERIDO",
                    "reason": "teste sintético",
                    "evidence": ["evidence/ops/exemplo.md"],
                    "conferred_by": "responsável sintético",
                    "conferred_at": date(2026, 10, 28),
                }
            ]
        }
    )
    monkeypatch.setattr(application, "load_registry", lambda path=None: registry)
    response = api_client.get(FISCAL_USE.format("indicador_sintetico"), headers=_headers())
    assert response.status_code == 200
    assert response.json()["usableForFiscalCalculation"] is True
    events = db_session.scalars(
        select(AuditEvent).where(AuditEvent.action == "indicator.fiscal_use")
    ).all()
    assert [event.outcome for event in events] == ["allowed"]
    # Qualquer outro indicador continua recusado com esse registro.
    assert (
        api_client.get(FISCAL_USE.format("sped_compras_uf"), headers=_headers()).status_code == 409
    )


@pytest.mark.parametrize("route", ["/v1/sped-operacoes", "/v1/tax-rates"])
def test_a_broken_registry_makes_the_reads_fail_instead_of_opening_the_gate(
    api_client, monkeypatch, tmp_path: Path, route
) -> None:
    broken = tmp_path / "indicator-reliability.yaml"
    broken.write_text("indicators: [{id: a, level: CONFERIDO, reason: r}]\n", encoding="utf-8")
    monkeypatch.setattr(application, "registry_path", lambda: broken)
    response = _lenient(api_client).get(route, headers=_headers())
    assert response.status_code == 500
    assert "reliability" not in response.text
    assert "CONFERIDO" not in response.text
    assert "Traceback" not in response.text
    assert "RegistryError" not in response.text


def test_a_missing_registry_also_fails_closed(api_client, monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(application, "registry_path", lambda: tmp_path / "nao-existe.yaml")
    client = _lenient(api_client)
    assert client.get("/v1/tax-rates", headers=_headers()).status_code == 500
    use = FISCAL_USE.format("icms_aliquota_ac")
    assert client.get(use, headers=_headers()).status_code == 500


def test_the_block_never_marks_an_exploratorio_or_nao_confiavel_as_usable(api_client) -> None:
    body = api_client.get("/v1/sped-operacoes?pageSize=1", headers=_headers()).json()
    assert body["reliability"]["indicators"]
    for item in body["reliability"]["indicators"]:
        assert item["usableForFiscalCalculation"] is False
        assert item["publishableInSimulator"] is False
        assert (item["level"] != "NAO_CONFIAVEL") == item["usableAsHypothesis"]
