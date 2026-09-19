from sirta_api.domain.municipal_uploads import (
    MUNICIPAL_UPLOADS_VERSION,
    build_municipal_uploads_panel,
)


def test_municipal_uploads_empty_shell_credential_required() -> None:
    assert MUNICIPAL_UPLOADS_VERSION.startswith("municipal-uploads-technical-")
    snap = build_municipal_uploads_panel()
    assert snap["binding"] is False
    assert snap["commandsDisabled"] is True
    assert snap["uploadEnabled"] is False
    assert snap["quarantineRequired"] is True
    assert snap["tenantScoped"] is True
    assert snap["createsTaxCredit"] is False
    assert snap["samplePresent"] is False
    assert snap["g0Status"] == "BLOCKED"
    assert snap["institutionalStatus"] == "CREDENTIAL_REQUIRED"
    assert snap["items"] == []
    assert snap["total"] == 0
    assert len(snap["slots"]) == 6
    assert all(slot["uploadEnabled"] is False for slot in snap["slots"])
    assert all(slot["samplePresent"] is False for slot in snap["slots"])
    source_ids = {slot["sourceId"] for slot in snap["slots"]}
    assert "MUNICIPAL-ISS-RESTRICTED" in source_ids
    assert "MUNICIPAL-IPTU-RESTRICTED" in source_ids
