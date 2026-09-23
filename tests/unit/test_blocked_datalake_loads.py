"""The recovery comparison stays unpublished until both official sides exist."""

from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.domain.catalog import ingest_allowed
from sirta_api.domain.dashboards import dashboard_by_id
from sirta_api.domain.gold import presentation_for
from sirta_api.domain.transfer_reconciliation import build_transfer_reconciliation_panel

BLOCKED_SOURCE_IDS = (
    "MUNICIPAL-ISS-RESTRICTED",
    "MUNICIPAL-IPTU-RESTRICTED",
    "MUNICIPAL-ITBI-RESTRICTED",
    "MUNICIPAL-DIVIDA-ATIVA",
    "MUNICIPAL-PAGAMENTOS",
    "MUNICIPAL-PROCESSOS",
    "PORTAL-TRANSPARENCIA-TRANSFERENCIAS",
    "RFB-DADOS-ABERTOS",
)


def test_restricted_and_credential_sources_stay_out_of_the_datalake() -> None:
    for source_id in BLOCKED_SOURCE_IDS:
        source = catalog_source(source_id)
        assert source is not None, source_id
        assert ingest_allowed(
            source_role=str(source["source_role"]),
            access_classification=str(source["access_classification"]),
            status=str(source["status"]),
            fixture_kind=str(source["fixture_kind"]),
        ) is False


def test_economic_context_is_not_an_iss_potential_formula() -> None:
    economia = dashboard_by_id("economia")
    assert economia is not None
    assert "não são potencial de ISS" in economia["emptyReason"]
    assert "potencial de ISS" in presentation_for("IBGE-SIDRA-PIB")["label"]
    assert "Não é base de ISS" in presentation_for("IBGE-SIDRA-CEMP")["label"]
    assert presentation_for("IBGE-SIDRA")["createsTaxCredit"] is False
    assert presentation_for("IBGE-SIDRA-PIB")["createsTaxCredit"] is False
    assert presentation_for("IBGE-SIDRA-CEMP")["createsTaxCredit"] is False


def test_transfer_expected_series_is_not_published_without_an_official_source() -> None:
    panel = build_transfer_reconciliation_panel()
    assert panel["expectedSources"] == []
    assert panel["compareOnlyWhenBothExist"] is True
    assert panel["createsTaxCredit"] is False
    assert catalog_source("TESOURO-FPM-PREVISTO") is None
    fpm = catalog_source("TESOURO-FPM-VALORES")
    assert fpm is not None
    assert fpm["source_role"] == "OFFICIAL_TRANSFER"
    assert "previsto" not in str(fpm.get("indicator") or "").lower()
