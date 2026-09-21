from sirta_api.domain.errors import ConflictError
from sirta_api.domain.sectoral_enrichment import (
    BLOCKED_SECTORAL_CONNECTORS,
    build_sectoral_enrichment_panel,
    reject_sectoral_enrichment_command,
)


def test_sectoral_panel_partial_anp_aneel_bcb_epe_anatel_cnes_activation() -> None:
    panel = build_sectoral_enrichment_panel()
    assert panel["createsTaxCredit"] is False
    assert panel["ingestEnabled"] is True
    assert panel["items"] == []
    assert panel["total"] == 0
    assert panel["sourceRole"] == "REFERENCE_ENRICHMENT"
    assert panel["institutionalStatus"] == "PARTIAL_TECHNICAL_ACTIVATION"
    assert len(panel["sources"]) == 9
    by_id = {row["sourceId"]: row for row in panel["sources"]}
    assert by_id["ANP-REVENDEDORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANP-REVENDEDORES"]["ingestAllowed"] is True
    assert by_id["ANEEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANEEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["BCB-SGS-OLINDA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-SGS-OLINDA"]["ingestAllowed"] is True
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["ingestAllowed"] is True
    assert by_id["BCB-OLINDA-EXPECTATIVAS-MENSAIS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-OLINDA-EXPECTATIVAS-MENSAIS"]["ingestAllowed"] is True
    assert by_id["BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS"]["ingestAllowed"] is True
    assert by_id["EPE-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["EPE-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["ANATEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANATEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["CNES-DATASUS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["CNES-DATASUS"]["ingestAllowed"] is True


def test_sectoral_connectors_remain_unblocked_after_cnes_activation() -> None:
    assert "anp_revendedores_api" not in BLOCKED_SECTORAL_CONNECTORS
    assert "aneel_ckan_open" not in BLOCKED_SECTORAL_CONNECTORS
    assert "bcb_sgs_olinda" not in BLOCKED_SECTORAL_CONNECTORS
    assert "bcb_olinda_expectativas" not in BLOCKED_SECTORAL_CONNECTORS
    assert "epe_open_files" not in BLOCKED_SECTORAL_CONNECTORS
    assert "anatel_dados_gov" not in BLOCKED_SECTORAL_CONNECTORS
    assert "cnes_datasus_open" not in BLOCKED_SECTORAL_CONNECTORS
    assert len(BLOCKED_SECTORAL_CONNECTORS) == 0


def test_sectoral_command_is_rejected() -> None:
    try:
        reject_sectoral_enrichment_command()
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")
