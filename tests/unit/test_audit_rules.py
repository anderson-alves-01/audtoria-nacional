from sirta_api.domain.audit_rules import (
    AUDIT_RULES_CATALOG,
    AUDIT_RULES_VERSION,
    build_audit_rules_catalog,
)


def test_audit_rules_catalog_is_non_binding_and_never_credit() -> None:
    assert AUDIT_RULES_VERSION.startswith("audit-rules-")
    assert AUDIT_RULES_CATALOG
    catalog = build_audit_rules_catalog()
    assert catalog["binding"] is False
    assert catalog["operational"] is False
    assert catalog["homologated"] is False
    assert catalog["createsTaxCredit"] is False
    assert catalog["taxPotentialAsCredit"] is False
    assert catalog["commandsDisabled"] is True
    assert all(item["binding"] is False for item in catalog["items"])
    assert all(item["status"] == "NON_BINDING" for item in catalog["items"])
    assert all(item["createsTaxCredit"] is False for item in catalog["items"])
