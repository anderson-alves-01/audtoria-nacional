from sirta_api.domain.errors import ConflictError
from sirta_api.domain.procuradoria_panel import (
    PROCURADORIA_PANEL_VERSION,
    build_procuradoria_panel,
    reject_legal_command,
)


def test_procuradoria_panel_is_empty_official_shell() -> None:
    assert PROCURADORIA_PANEL_VERSION.startswith("procuradoria-panel-technical-")
    panel = build_procuradoria_panel()
    assert panel["binding"] is False
    assert panel["operational"] is False
    assert panel["homologated"] is False
    assert panel["commandsDisabled"] is True
    assert panel["legalCommandsEnabled"] is False
    assert panel["altersLegalStatus"] is False
    assert panel["createsTaxCredit"] is False
    assert panel["items"] == []
    assert panel["queue"] == []
    assert panel["g0Status"] == "BLOCKED"
    assert panel["g5Status"] == "BLOCKED"
    assert panel["g6Status"] == "LOCAL_GO_OFFICIAL_BLOCKED"


def test_legal_command_is_rejected() -> None:
    try:
        reject_legal_command()
        raise AssertionError("expected ConflictError")
    except ConflictError as exc:
        assert exc.status == 409
