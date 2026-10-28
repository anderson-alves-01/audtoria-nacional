from tests.helpers.sped_fixture import build_sped_workbook
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
)

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _headers(subject=USER_ANALYST_ALPHA) -> dict[str, str]:
    return auth_headers(
        subject=subject,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_fiscal_use_is_refused_with_409_for_every_non_conferido_indicator(api_client) -> None:
    for indicator_id in (
        "sped_quantidade_uf_cfop_ano",  # NAO_CONFIAVEL
        "sped_compras_uf",  # NAO_CONFIAVEL
        "sped_quantidade_uf_ano",  # EXPLORATORIO
        "icms_aliquota_demais_uf",  # EXPLORATORIO
        "indicador-inexistente",  # nao registrado: falha fechada
    ):
        response = api_client.get(
            f"/v1/indicator-reliability/{indicator_id}/fiscal-use", headers=_headers()
        )
        assert response.status_code == 409, indicator_id
        assert indicator_id in response.json()["detail"]


def test_fiscal_use_requires_authentication_and_fiscal_read(api_client) -> None:
    url = "/v1/indicator-reliability/sped_compras_uf/fiscal-use"
    assert api_client.get(url, headers={}).status_code == 401
    assert api_client.get(url, headers=_headers(USER_ADMIN_ALPHA)).status_code == 403


def test_sped_read_exposes_the_reliability_block_without_changing_other_fields(api_client) -> None:
    upload = api_client.post(
        "/v1/data-sources/SPED-NFE-UF-CFOP/upload",
        content=build_sped_workbook(),
        headers={**_headers(USER_ADMIN_ALPHA), "Content-Type": XLSX},
    )
    assert upload.status_code == 200, upload.text
    body = api_client.get("/v1/sped-operacoes", headers=_headers()).json()
    assert body["homologated"] is False and body["published"] is False
    block = body["reliability"]
    assert block["levels"] == ["NAO_CONFIAVEL", "EXPLORATORIO", "CONFERIDO"]
    by_id = {item["id"]: item for item in block["indicators"]}
    assert by_id["sped_compras_uf"]["level"] == "NAO_CONFIAVEL"
    assert by_id["sped_quantidade_uf_ano"]["level"] == "EXPLORATORIO"
    assert all(item["usableForFiscalCalculation"] is False for item in by_id.values())
    assert all(item["publishableInSimulator"] is False for item in by_id.values())
    assert by_id["sped_valor_estimado_uf_cfop_ano"]["usableAsHypothesis"] is False


def test_tax_rates_expose_that_no_rate_indicator_is_homologated(api_client) -> None:
    body = api_client.get("/v1/tax-rates?tax=ICMS&uf=SP", headers=_headers()).json()
    indicators = body["reliability"]["indicators"]
    assert {item["id"] for item in indicators} == {
        "icms_aliquota_ac",
        "icms_aliquota_demais_uf",
        "itcd_itbi_iss_aliquotas",
    }
    assert all(item["level"] == "EXPLORATORIO" for item in indicators)
    assert all(item["usableForFiscalCalculation"] is False for item in indicators)
