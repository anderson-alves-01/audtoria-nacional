from sirta_api.domain.collection_panel import COLLECTION_PANEL_VERSION, build_collection_panel


def test_collection_panel_is_empty_official_shell() -> None:
    assert COLLECTION_PANEL_VERSION.startswith("collection-panel-technical-")
    panel = build_collection_panel()
    assert panel["binding"] is False
    assert panel["operational"] is False
    assert panel["homologated"] is False
    assert panel["commandsDisabled"] is True
    assert panel["sendEnabled"] is False
    assert panel["createsTaxCredit"] is False
    assert panel["items"] == []
    assert panel["queue"] == []
    assert panel["g0Status"] == "BLOCKED"
    assert panel["g4Status"] == "BLOCKED"
    assert panel["g5Status"] == "BLOCKED"
