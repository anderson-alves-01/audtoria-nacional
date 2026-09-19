from sirta_api.domain.gates import load_flags, program_snapshot


def test_feature_flags_are_disabled() -> None:
    flags = load_flags()
    assert flags["official_tesouro_connectors"] is False
    assert flags["official_ibs_cbs_rules"] is False
    assert flags["real_data_ingestion"] is False
    assert flags["production_deploy"] is False
    assert flags["cloud_apply"] is False


def test_program_snapshot_does_not_fabricate_approval() -> None:
    snapshot = program_snapshot()
    assert snapshot["humanApprovalFabricated"] is False
    assert snapshot["canApprove"] is False
    by_id = {item["id"]: item for item in snapshot["gates"]}
    assert by_id["G0"]["status"] == "BLOCKED"
    assert by_id["G1"]["status"] == "BLOCKED"
    assert all(item["met"] is False for item in by_id["G0"]["checklist"])
    assert all(item["met"] is False for item in by_id["G1"]["checklist"])
    assert by_id["G4"]["status"] == "BLOCKED"
    assert by_id["G7"]["officialStatus"] == "OFFICIAL_BLOCKED"
    assert by_id["G8"]["homologated"] is False
    assert by_id["G8"]["binding"] is False
    assert by_id["G8"]["operational"] is False
    assert by_id["G8"]["officialStatus"] == "OFFICIAL_BLOCKED"
    assert by_id["G9"]["status"] == "BLOCKED"
    assert by_id["G10"]["status"] == "BLOCKED"
