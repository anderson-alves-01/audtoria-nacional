from sirta_api.domain.errors import ConflictError
from sirta_api.domain.payments_panel import (
    PAYMENTS_PANEL_VERSION,
    build_payments_panel,
    reject_payment_command,
)


def test_payments_panel_is_empty_official_shell() -> None:
    assert PAYMENTS_PANEL_VERSION.startswith("payments-panel-technical-")
    panel = build_payments_panel()
    assert panel["binding"] is False
    assert panel["operational"] is False
    assert panel["homologated"] is False
    assert panel["commandsDisabled"] is True
    assert panel["recoveryInvented"] is False
    assert panel["createsTaxCredit"] is False
    assert panel["items"] == []
    assert panel["installments"] == []
    assert panel["g0Status"] == "BLOCKED"
    assert panel["g5Status"] == "BLOCKED"
    assert panel["g6Status"] == "LOCAL_GO_OFFICIAL_BLOCKED"


def test_payment_command_is_rejected() -> None:
    try:
        reject_payment_command()
        raise AssertionError("expected ConflictError")
    except ConflictError as exc:
        assert exc.status == 409
