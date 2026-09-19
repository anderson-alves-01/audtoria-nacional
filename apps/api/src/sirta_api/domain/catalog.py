from sirta_api.domain.errors import ConflictError, ForbiddenError

ROLES = frozenset({"PRIMARY_FISCAL", "OFFICIAL_TRANSFER", "REFERENCE_ENRICHMENT", "REGULATORY"})
ACCESS = frozenset({"PUBLIC_OPEN", "PUBLIC_CONTROLLED", "RESTRICTED", "CONFIDENTIAL"})
LEGACY_STATUSES = frozenset({"UNDER_REVIEW", "APPROVED"})
STATUSES = frozenset(
    {
        "DISCOVERED",
        "PROVENANCE_VERIFIED",
        "TECHNICALLY_APPROVED",
        "ACTIVE",
        "SUSPENDED",
        "CREDENTIAL_REQUIRED",
        "UNAVAILABLE",
        "RETIRED",
        "OFFICIAL_BLOCKED",
        "READY_FOR_TERRITORIAL_SCOPE",
        *LEGACY_STATUSES,
    }
)
OFFICIAL_INGESTIBLE = frozenset({"TECHNICALLY_APPROVED", "ACTIVE"})
SYNTHETIC_INGESTIBLE = frozenset({"APPROVED", "ACTIVE"})
RESTRICTED_ACCESS = frozenset({"RESTRICTED", "CONFIDENTIAL"})
HOMOLOGATION_PENDING = "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
OFFICIAL_BANNER = (
    "DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE"
)


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
    allow_synthetic_loads: bool = False,
) -> bool:
    validate_source(
        source_role=source_role, access_classification=access_classification, status=status
    )
    if access_classification in RESTRICTED_ACCESS:
        return False
    if fixture_kind == "OFFICIAL":
        return (
            access_classification == "PUBLIC_OPEN"
            and status in OFFICIAL_INGESTIBLE
            and source_role != "PRIMARY_FISCAL"
        )
    if fixture_kind == "SYNTHETIC":
        return allow_synthetic_loads and status in SYNTHETIC_INGESTIBLE
    return False


def assert_ingest_allowed(**kwargs) -> None:
    if not ingest_allowed(**kwargs):
        raise ForbiddenError("Ingestion is not allowed for this source")


def creates_tax_credit(_source_role: str) -> bool:
    return False
