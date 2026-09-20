from sirta_api.domain.errors import ConflictError
from sirta_api.domain.state_transfers import (
    build_state_transfers_panel,
    reject_state_transfers_command,
)


def test_state_transfers_panel_empty_and_non_credit() -> None:
    panel = build_state_transfers_panel()
    assert panel["createsTaxCredit"] is False
    assert panel["items"] == []
    assert panel["total"] == 0
    assert panel["verifiedCount"] >= 3
    by_uf = {row["uf"]: row for row in panel["states"]}
    assert by_uf["PE"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["PE"]["ingestAllowed"] is True
    assert by_uf["BA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["BA"]["ingestAllowed"] is True
    assert by_uf["MG"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["MG"]["ingestAllowed"] is True
    assert by_uf["RO"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["RO"]["ingestAllowed"] is True
    assert by_uf["AL"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["AL"]["ingestAllowed"] is True
    assert by_uf["PI"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["PI"]["ingestAllowed"] is True
    assert by_uf["SE"]["status"] == "PROVENANCE_VERIFIED"
    assert by_uf["RJ"]["status"] == "PROVENANCE_VERIFIED"
    assert by_uf["SP"]["status"] == "DISCOVERED"
    assert panel["ingestEnabled"] is True


def test_state_transfers_command_rejected() -> None:
    try:
        reject_state_transfers_command()
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")
