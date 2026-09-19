from sirta_api.domain.errors import ConflictError
from sirta_api.domain.transfer_reconciliation import (
    TRANSFER_RECONCILIATION_VERSION,
    build_transfer_reconciliation_panel,
    reject_reconciliation_command,
)


def test_transfer_reconciliation_is_empty_occurrence_only_shell() -> None:
    assert TRANSFER_RECONCILIATION_VERSION.startswith("transfer-reconciliation-technical-")
    panel = build_transfer_reconciliation_panel()
    assert panel["binding"] is False
    assert panel["operational"] is False
    assert panel["homologated"] is False
    assert panel["commandsDisabled"] is True
    assert panel["autoReconcileEnabled"] is False
    assert panel["createsTaxCredit"] is False
    assert panel["differenceIsOccurrenceOnly"] is True
    assert panel["compareOnlyWhenBothExist"] is True
    assert panel["items"] == []
    assert panel["differences"] == []
    assert panel["expectedSources"] == []
    assert panel["receivedSources"] == []
    assert panel["g7Status"] == "LOCAL_GO_OFFICIAL_BLOCKED"


def test_reconciliation_command_is_rejected() -> None:
    try:
        reject_reconciliation_command()
        raise AssertionError("expected ConflictError")
    except ConflictError as exc:
        assert exc.status == 409
