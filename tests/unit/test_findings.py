from sirta_api.domain.findings import FINDINGS_VERSION, build_findings_page


def test_findings_page_is_empty_and_never_credit() -> None:
    assert FINDINGS_VERSION.startswith("findings-technical-")
    page = build_findings_page()
    assert page["binding"] is False
    assert page["operational"] is False
    assert page["homologated"] is False
    assert page["commandsDisabled"] is True
    assert page["createsTaxCredit"] is False
    assert page["legalCommandsEnabled"] is False
    assert page["items"] == []
    assert page["total"] == 0
    assert page["g5Status"] == "BLOCKED"
    assert "crédito" in page["disclaimer"].lower() or "credito" in page["disclaimer"].lower()
