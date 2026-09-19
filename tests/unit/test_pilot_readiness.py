from sirta_api.domain.pilot_readiness import (
    PILOT_READINESS_VERSION,
    build_pilot_readiness_snapshot,
)


def test_pilot_readiness_technical_ready_g9_blocked() -> None:
    assert PILOT_READINESS_VERSION.startswith("pilot-readiness-technical-")
    snap = build_pilot_readiness_snapshot()
    assert snap["binding"] is False
    assert snap["commandsDisabled"] is True
    assert snap["createsTaxCredit"] is False
    assert snap["pilotMunicipalityApproved"] is False
    assert snap["technicalReady"] is True
    assert snap["institutionalReady"] is False
    assert snap["g9Status"] == "BLOCKED"
    assert snap["g10Status"] == "BLOCKED"
    assert snap["items"] == []
    assert any(row["id"] == "pilot_municipality" and row["met"] is False for row in snap["checklist"])
    assert any(row["id"] == "ci_reproducible" and row["met"] is True for row in snap["checklist"])
