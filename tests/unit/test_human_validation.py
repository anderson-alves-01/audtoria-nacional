from sirta_api.domain.human_validation import (
    HUMAN_VALIDATION_VERSION,
    REFERENCE_STATES,
    build_human_validation_snapshot,
)


def test_human_validation_workflow_is_empty_and_non_public() -> None:
    assert HUMAN_VALIDATION_VERSION.startswith("human-validation-workflow-")
    snapshot = build_human_validation_snapshot()
    assert snapshot["binding"] is False
    assert snapshot["commandsDisabled"] is True
    assert snapshot["createsTaxCredit"] is False
    assert snapshot["publishesPublicCredit"] is False
    assert snapshot["legalCommandsEnabled"] is False
    assert snapshot["activeItems"] == []
    assert snapshot["queue"] == []
    assert snapshot["g4Status"] == "BLOCKED"
    assert snapshot["g5Status"] == "BLOCKED"
    assert list(REFERENCE_STATES) == snapshot["referenceStates"]
    assert "IDENTIFIED" in snapshot["referenceStates"]
    assert "VALIDATED" in snapshot["referenceStates"]
