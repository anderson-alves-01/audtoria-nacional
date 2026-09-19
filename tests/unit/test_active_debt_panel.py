from sirta_api.domain.active_debt_panel import (
    ACTIVE_DEBT_PANEL_VERSION,
    build_active_debt_panel,
    reject_inscription_command,
)
from sirta_api.domain.errors import ConflictError


def test_active_debt_panel_is_empty_official_shell() -> None:
    assert ACTIVE_DEBT_PANEL_VERSION.startswith("active-debt-panel-technical-")
    panel = build_active_debt_panel()
    assert panel["binding"] is False
    assert panel["operational"] is False
    assert panel["homologated"] is False
    assert panel["commandsDisabled"] is True
    assert panel["inscriptionEnabled"] is False
    assert panel["createsTaxCredit"] is False
    assert panel["legalCommandsEnabled"] is False
    assert panel["items"] == []
    assert panel["queue"] == []
    assert panel["g0Status"] == "BLOCKED"
    assert panel["g5Status"] == "BLOCKED"
    assert panel["g6Status"] == "LOCAL_GO_OFFICIAL_BLOCKED"


def test_inscription_command_is_rejected() -> None:
    try:
        reject_inscription_command()
        raise AssertionError("expected ConflictError")
    except ConflictError as exc:
        assert exc.status == 409
