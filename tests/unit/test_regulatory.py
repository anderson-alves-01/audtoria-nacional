from sirta_api.domain.errors import ConflictError
from sirta_api.domain.regulatory import (
    STATUS_NON_BINDING,
    SYNTHETIC_CATALOG,
    assert_not_operational,
    operational_use_allowed,
)


def test_synthetic_catalog_is_never_binding() -> None:
    assert SYNTHETIC_CATALOG
    assert all(item.version == "catalog-synthetic-v1" for item in SYNTHETIC_CATALOG)
    assert all(item.code for item in SYNTHETIC_CATALOG)


def test_operational_use_is_denied_without_homologation() -> None:
    allowed = operational_use_allowed(binding=False, status=STATUS_NON_BINDING, homologated=False)
    assert allowed is False
    try:
        assert_not_operational(binding=False, status=STATUS_NON_BINDING, homologated=False)
    except ConflictError as exc:
        assert "homologation" in exc.detail.lower()
        return
    raise AssertionError("expected ConflictError")


def test_simulation_cannot_become_operational_kpi() -> None:
    simulation = next(item for item in SYNTHETIC_CATALOG if item.kind == "SIMULATION")
    assert "KPI" in simulation.notes
    allowed = operational_use_allowed(binding=True, status=STATUS_NON_BINDING, homologated=False)
    assert allowed is False
