from sirta_api.domain.catalog import assert_ingest_allowed, creates_tax_credit, validate_source
from sirta_api.domain.errors import ConflictError, ForbiddenError


def test_public_source_cannot_be_primary_fiscal() -> None:
    try:
        validate_source(
            source_role="PRIMARY_FISCAL",
            access_classification="PUBLIC_OPEN",
            status="DISCOVERED",
        )
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")


def test_restricted_source_cannot_ingest() -> None:
    try:
        assert_ingest_allowed(
            source_role="PRIMARY_FISCAL",
            access_classification="RESTRICTED",
            status="APPROVED",
            fixture_kind="SYNTHETIC",
        )
    except ForbiddenError:
        return
    raise AssertionError("expected ForbiddenError")


def test_synthetic_reference_source_may_dry_run() -> None:
    from sirta_api.domain.catalog import ingest_allowed

    assert ingest_allowed(
        source_role="REFERENCE_ENRICHMENT",
        access_classification="PUBLIC_OPEN",
        status="APPROVED",
        fixture_kind="SYNTHETIC",
    )
    assert creates_tax_credit("REFERENCE_ENRICHMENT") is False
    assert creates_tax_credit("OFFICIAL_TRANSFER") is False
