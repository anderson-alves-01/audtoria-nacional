"""Public continuation stays a five-ente slice. Empty and restricted sources stay out."""

import pytest

from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.domain.backfill_controls import clamp_max_entes, select_entes_slice
from sirta_api.domain.catalog import ingest_allowed
from sirta_api.domain.errors import ConflictError

CONTINUATION = ("SICONFI-RREO", "SICONFI-DCA")
SKIPPED_EMPTY = (
    "TESOURO-FEX-VALORES",
    "ESTADO-MG-ICMS-QUOTA",
    "ESTADO-MG-IPVA-QUOTA",
    "ESTADO-MG-IPI-QUOTA",
    "SICONFI-RGF",
)
RESTRICTED_MUNICIPAL = (
    "MUNICIPAL-ISS-RESTRICTED",
    "MUNICIPAL-IPTU-RESTRICTED",
    "MUNICIPAL-ITBI-RESTRICTED",
)


def test_rreo_and_dca_slices_are_capped_at_five_entes() -> None:
    for source_id in CONTINUATION:
        source = catalog_source(source_id)
        assert source is not None
        assert source["parameters"]["max_entes_per_run"] == 5
        assert source["access_classification"] == "PUBLIC_OPEN"
        assert ingest_allowed(
            source_role=source["source_role"],
            access_classification=source["access_classification"],
            status=source["status"],
            fixture_kind=source["fixture_kind"],
        )
    assert clamp_max_entes(5, hard_cap=25) == 5
    selected, _skip, exhausted = select_entes_slice(
        [str(code) for code in range(100)], skip=5, max_entes=5
    )
    assert len(selected) == 5
    assert exhausted is False
    try:
        clamp_max_entes(26, hard_cap=25)
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")


def test_empty_public_sources_are_outside_the_continuation() -> None:
    fex = catalog_source("TESOURO-FEX-VALORES")
    rgf = catalog_source("SICONFI-RGF")
    assert fex is not None and fex["competence"] == "2025-01"
    assert rgf is not None
    assert rgf["parameters"]["query"]["nr_periodo"] == "3"
    for source_id in SKIPPED_EMPTY:
        assert source_id not in CONTINUATION
        assert catalog_source(source_id) is not None


def test_municipal_iss_iptu_itbi_stay_blocked_until_dpa() -> None:
    for source_id in RESTRICTED_MUNICIPAL:
        source = catalog_source(source_id)
        assert source is not None
        assert source["access_classification"] == "RESTRICTED"
        assert source_id not in CONTINUATION
        assert (
            ingest_allowed(
                source_role=source["source_role"],
                access_classification=source["access_classification"],
                status=source["status"],
                fixture_kind=source["fixture_kind"],
            )
            is False
        )


def test_national_backfill_above_the_hard_cap_is_rejected() -> None:
    with pytest.raises(ConflictError):
        clamp_max_entes(5570, hard_cap=25)
