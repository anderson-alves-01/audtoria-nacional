from sirta_api.domain.errors import ConflictError
from sirta_api.domain.sectoral_enrichment import (
    BLOCKED_SECTORAL_CONNECTORS,
    build_sectoral_enrichment_panel,
    reject_sectoral_enrichment_command,
)


def test_sectoral_panel_is_empty_and_non_credit() -> None:
    panel = build_sectoral_enrichment_panel()
    assert panel["createsTaxCredit"] is False
    assert panel["ingestEnabled"] is False
    assert panel["items"] == []
    assert panel["total"] == 0
    assert panel["sourceRole"] == "REFERENCE_ENRICHMENT"
    assert len(panel["sources"]) == 6
    assert all(row["ingestAllowed"] is False for row in panel["sources"])
    assert all(row["status"] == "DISCOVERED" for row in panel["sources"])


def test_sectoral_connectors_are_blocked() -> None:
    assert "anp_revendedores_api" in BLOCKED_SECTORAL_CONNECTORS
    assert "cnes_datasus_open" in BLOCKED_SECTORAL_CONNECTORS
    assert len(BLOCKED_SECTORAL_CONNECTORS) == 6


def test_sectoral_command_is_rejected() -> None:
    try:
        reject_sectoral_enrichment_command()
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")
