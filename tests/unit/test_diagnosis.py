from sirta_api.domain.diagnosis import (
    DIAGNOSIS_CHECKLIST,
    DIAGNOSIS_VERSION,
    build_diagnosis_snapshot,
)


def test_diagnosis_checklist_has_no_recovery_meta_and_all_unmet() -> None:
    assert DIAGNOSIS_VERSION.startswith("diagnosis-technical-")
    assert DIAGNOSIS_CHECKLIST
    assert all(item["met"] is False for item in DIAGNOSIS_CHECKLIST)
    snapshot = build_diagnosis_snapshot()
    assert snapshot["binding"] is False
    assert snapshot["operational"] is False
    assert snapshot["homologated"] is False
    assert snapshot["commandsDisabled"] is True
    assert snapshot["recoveryMeta"] is None
    assert "recoveryTarget" not in snapshot
    assert "recoveryPercent" not in snapshot
    assert snapshot["items"] == []
    assert all(row["met"] is False for row in snapshot["checklist"])
    assert (
        "recuperação" in snapshot["disclaimer"].lower()
        or "recovery" in snapshot["disclaimer"].lower()
    )
