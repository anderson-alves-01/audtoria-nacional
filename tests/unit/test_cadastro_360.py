from sirta_api.domain.cadastro_360 import CADASTRO_360_VERSION, build_cadastro_360_panel


def test_cadastro_360_empty_shell_no_pii() -> None:
    assert CADASTRO_360_VERSION.startswith("cadastro-360-technical-")
    snap = build_cadastro_360_panel()
    assert snap["binding"] is False
    assert snap["commandsDisabled"] is True
    assert snap["createsTaxCredit"] is False
    assert snap["piiPresent"] is False
    assert snap["territoryInvented"] is False
    assert snap["minimizationEnforced"] is True
    assert snap["rfbScopeReady"] is False
    assert snap["municipalDataLinked"] is False
    assert snap["g0Status"] == "BLOCKED"
    assert snap["institutionalStatus"] == "CREDENTIAL_REQUIRED"
    assert snap["subjects"] == []
    assert snap["items"] == []
    assert snap["total"] == 0
    fields = {row["field"] for row in snap["minimizationPolicy"]}
    assert "cpf_cnpj" in fields
    assert all(row["present"] is False for row in snap["minimizationPolicy"])
