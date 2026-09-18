from sirta_api.domain.errors import ConflictError, ForbiddenError

ROLES = frozenset({"PRIMARY_FISCAL", "OFFICIAL_TRANSFER", "REFERENCE_ENRICHMENT", "REGULATORY"})
ACCESS = frozenset({"PUBLIC_OPEN", "PUBLIC_CONTROLLED", "RESTRICTED", "CONFIDENTIAL"})
STATUSES = frozenset({"DISCOVERED", "UNDER_REVIEW", "APPROVED", "ACTIVE", "SUSPENDED", "RETIRED"})
INGESTIBLE = frozenset({"APPROVED", "ACTIVE"})
RESTRICTED_ACCESS = frozenset({"RESTRICTED", "CONFIDENTIAL"})


def validate_source(*, source_role: str, access_classification: str, status: str) -> None:
    if source_role not in ROLES:
        raise ConflictError("sourceRole is not supported")
    if access_classification not in ACCESS:
        raise ConflictError("accessClassification is not supported")
    if status not in STATUSES:
        raise ConflictError("status is not supported")
    if source_role == "PRIMARY_FISCAL" and access_classification.startswith("PUBLIC_"):
        raise ConflictError("A public source cannot be classified as PRIMARY_FISCAL")


def ingest_allowed(
    *,
    source_role: str,
    access_classification: str,
    status: str,
    fixture_kind: str,
) -> bool:
    validate_source(
        source_role=source_role, access_classification=access_classification, status=status
    )
    if access_classification in RESTRICTED_ACCESS:
        return False
    if status not in INGESTIBLE:
        return False
    return fixture_kind == "SYNTHETIC"


def assert_ingest_allowed(**kwargs) -> None:
    if not ingest_allowed(**kwargs):
        raise ForbiddenError("Ingestion is not allowed for this source")


def creates_tax_credit(_source_role: str) -> bool:
    return False
