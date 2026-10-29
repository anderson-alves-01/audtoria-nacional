"""Controle de acesso, erros seguros, auditoria e ausência de publicação automática do Simulador.

Cobre as três rotas que o Simulador consome: SPED, tabela de alíquotas e uso fiscal do indicador.
Dados sintéticos apenas.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy import select
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.models import AuditEvent
from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    PURPOSE_BETA_ACTIVE,
    TENANT_ALPHA,
    TENANT_BETA,
    TERRITORY_ALPHA_CENTRO,
    TERRITORY_BETA_SEDE,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
    USER_ANALYST_BETA,
)
from sirta_api.entrypoints.main import app

ROOT = Path(__file__).resolve().parents[2]
ROUTES = (
    "/v1/sped-operacoes",
    "/v1/tax-rates",
    "/v1/indicator-reliability/sped_compras_uf/fiscal-use",
    "/v1/cgu-nfe",
)


def _alpha(subject) -> dict[str, str]:
    return auth_headers(
        subject=subject,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _analyst() -> dict[str, str]:
    return _alpha(USER_ANALYST_ALPHA)


def _admin() -> dict[str, str]:
    return _alpha(USER_ADMIN_ALPHA)


def _assert_safe_error(response) -> None:
    """Erro sem rastro de pilha, caminho de arquivo, SQL, credencial ou segredo."""
    text = response.text
    assert "Traceback" not in text
    assert 'File "' not in text
    assert not re.search(r"[A-Za-z]:\\\\|/home/|/app/|site-packages", text)
    assert not re.search(r"(?i)select .* from|psycopg|sqlalchemy|postgresql://|password", text)
    assert not re.search(r"(?i)bearer\s+ey", text)


@pytest.mark.parametrize("route", ROUTES)
def test_every_route_requires_a_session(api_client, route) -> None:
    response = api_client.get(route)
    assert response.status_code == 401
    _assert_safe_error(response)
    assert response.json().get("traceId")


@pytest.mark.parametrize("route", ROUTES)
def test_malformed_and_foreign_tokens_are_refused(api_client, route) -> None:
    for authorization in (
        "Bearer",
        "Bearer ",
        "Bearer not-a-jwt",
        "Basic dXNlcjpwYXNz",
        "bearer.x.y",
    ):
        response = api_client.get(route, headers={"Authorization": authorization})
        assert response.status_code in (401, 403), authorization
        _assert_safe_error(response)


@pytest.mark.parametrize("route", ROUTES)
def test_territory_and_purpose_are_required(api_client, route) -> None:
    headers = _analyst()
    for missing in ("X-Territory-Id", "X-Purpose-Id"):
        partial = {key: value for key, value in headers.items() if key != missing}
        response = api_client.get(route, headers=partial)
        assert response.status_code == 403, missing
        _assert_safe_error(response)


@pytest.mark.parametrize("route", ROUTES)
def test_another_tenant_cannot_use_the_territory_or_purpose_of_this_one(api_client, route) -> None:
    beta_with_alpha_territory = auth_headers(
        subject=USER_ANALYST_BETA,
        tenant_id=TENANT_BETA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_BETA_ACTIVE,
    )
    beta_with_alpha_purpose = auth_headers(
        subject=USER_ANALYST_BETA,
        tenant_id=TENANT_BETA,
        territory_id=TERRITORY_BETA_SEDE,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    token_of_other_tenant = auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_BETA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    for headers in (beta_with_alpha_territory, beta_with_alpha_purpose, token_of_other_tenant):
        response = api_client.get(route, headers=headers)
        assert response.status_code == 403
        _assert_safe_error(response)


@pytest.mark.parametrize("route", ROUTES)
def test_technical_administrator_without_operator_login_cannot_read_fiscal_content(
    api_client, route
) -> None:
    response = api_client.get(route, headers=_admin())
    assert response.status_code == 403
    _assert_safe_error(response)


def test_validation_and_conflict_errors_are_safe_and_carry_a_trace_id(api_client) -> None:
    invalid = api_client.get("/v1/tax-rates?tax=XYZ", headers=_analyst())
    assert invalid.status_code == 422
    conflict = api_client.get(ROUTES[2], headers=_analyst())
    assert conflict.status_code == 409
    for response in (invalid, conflict):
        _assert_safe_error(response)
        assert response.json()["traceId"]
        assert response.headers["content-type"].startswith("application/problem+json")


def test_reading_the_rate_table_is_audited(api_client, db_session) -> None:
    assert api_client.get("/v1/tax-rates", headers=_analyst()).status_code == 200
    events = db_session.scalars(
        select(AuditEvent).where(AuditEvent.action == "tax_rates.list")
    ).all()
    assert len(events) == 1
    assert events[0].outcome == "allowed"
    assert events[0].tenant_id == TENANT_ALPHA
    assert events[0].route == "/v1/tax-rates"


def test_cgu_nfe_fiscal_use_is_allowed_and_sped_is_still_refused(api_client) -> None:
    conferred = api_client.get(
        "/v1/indicator-reliability/cgu_nfe_itens_uf_ano/fiscal-use", headers=_analyst()
    )
    assert conferred.status_code == 200
    assert conferred.json()["level"] == "CONFERIDO"
    refused = api_client.get(ROUTES[2], headers=_analyst())
    assert refused.status_code == 409


def test_a_refused_fiscal_use_is_audited_even_though_the_request_fails(
    api_client, db_session
) -> None:
    response = api_client.get(ROUTES[2], headers=_analyst())
    assert response.status_code == 409
    db_session.expire_all()
    events = db_session.scalars(
        select(AuditEvent).where(AuditEvent.action == "indicator.fiscal_use")
    ).all()
    assert len(events) == 1
    assert events[0].outcome == "denied"
    assert events[0].tenant_id == TENANT_ALPHA
    assert events[0].resource_type == "indicator"


def test_audit_events_never_store_secrets_or_payloads(api_client, db_session) -> None:
    api_client.get("/v1/tax-rates", headers=_analyst())
    api_client.get(ROUTES[2], headers=_analyst())
    for event in db_session.scalars(select(AuditEvent)).all():
        text = " ".join(str(value) for value in vars(event).values())
        assert "Bearer" not in text
        assert "eyJ" not in text


def test_no_route_of_the_simulator_can_publish_or_promote_anything(api_client) -> None:
    prefixes = ("/v1/sped-operacoes", "/v1/tax-rates", "/v1/indicator-reliability")
    for route in app.routes:
        path = getattr(route, "path", "")
        if path.startswith(prefixes):
            assert set(route.methods or ()) <= {"GET", "HEAD"}, path
    # Métodos de escrita não existem nem por engano.
    for method in (api_client.post, api_client.put, api_client.patch, api_client.delete):
        for route in ROUTES:
            assert method(route, headers=_analyst()).status_code in (404, 405)


def test_no_code_promotes_an_indicator_or_publishes_the_sped_load() -> None:
    import yaml

    registry_path = ROOT / "config" / "indicator-reliability.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    conferred = [item["id"] for item in registry["indicators"] if item["level"] == "CONFERIDO"]
    assert conferred == ["cgu_nfe_itens_uf_ano", "cgu_nfe_valor_itens_uf_ano"]
    assert all(not item.startswith("sped_") for item in conferred)
    offenders = []
    for folder in ("apps/api/src", "tools"):
        for path in (ROOT / folder).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            writes_registry = re.search(
                r"indicator-reliability\.yaml[^\n]*\)\s*\.write_text|open\([^)]*indicator-reliability",
                text,
            )
            promotes = re.search(r"level\W+CONFERIDO\W+(?:conferred|=)", text) and "yaml" in text
            if writes_registry or promotes:
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
    sped_ingest = (ROOT / "apps/api/src/sirta_api/application/sped_ingest.py").read_text(
        encoding="utf-8"
    )
    assert not re.search(r"published\s*=\s*True|\"published\":\s*True", sped_ingest)
    assert not re.search(r"homologated\s*=\s*True|\"homologated\":\s*True", sped_ingest)


def test_environments_are_segregated_in_the_repository() -> None:
    """Segredos ficam fora do Git: só a chave de teste sintética e o modelo .env.example."""
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    env_files = [path for path in tracked if re.search(r"(^|/)\.env(\.|$)", path)]
    assert env_files == [".env.example"]
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"(?m)^\.env$", gitignore)
    keys = subprocess.run(
        ["git", "grep", "-l", "-E", "BEGIN [A-Z ]*PRIVATE KEY"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.splitlines()
    assert set(keys) <= {"tests/fixtures/jwt/private.pem", "apps/api/src/sirta_api/domain/dlp.py"}
