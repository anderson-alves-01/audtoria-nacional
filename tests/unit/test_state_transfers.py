from sirta_api.domain.errors import ConflictError
from sirta_api.domain.state_transfers import (
    build_state_transfers_panel,
    reject_state_transfers_command,
)


def test_state_transfers_panel_empty_and_non_credit() -> None:
    panel = build_state_transfers_panel()
    assert panel["createsTaxCredit"] is False
    assert panel["ingestEnabled"] is False
    assert panel["items"] == []
    assert panel["total"] == 0
    assert panel["verifiedCount"] >= 1
    by_uf = {row["uf"]: row for row in panel["states"]}
    assert by_uf["RJ"]["status"] == "PROVENANCE_VERIFIED"
    assert by_uf["RJ"]["ingestAllowed"] is False
    assert by_uf["SP"]["status"] == "DISCOVERED"
    assert all(row["ingestAllowed"] is False for row in panel["states"])


def test_state_transfers_command_rejected() -> None:
    try:
        reject_state_transfers_command()
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")
