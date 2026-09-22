from sirta_api.domain.ops_governance import OPS_GOVERNANCE_VERSION, build_ops_governance_snapshot


def test_ops_governance_runbooks_complete_g10_blocked() -> None:
    assert OPS_GOVERNANCE_VERSION.startswith("ops-governance-technical-")
    snap = build_ops_governance_snapshot()
    assert snap["binding"] is False
    assert snap["commandsDisabled"] is True
    assert snap["canDeploy"] is False
    assert snap["canApprove"] is False
    assert snap["humanApprovalFabricated"] is False
    assert snap["terraformApplyAuthorized"] is False
    assert snap["g10Status"] == "BLOCKED"
    assert snap["runbooksComplete"] is True
    assert snap["items"] == []
    paths = {row["path"] for row in snap["runbooks"]}
    assert "docs/operations/incident-response-local.md" in paths
    assert "docs/operations/ingest-ops-local.md" in paths
    assert "docs/operations/gates-governance-local.md" in paths
