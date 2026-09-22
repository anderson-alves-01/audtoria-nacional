"""Human validation workflow shell (F5). Not institutional Gold homologation."""

HUMAN_VALIDATION_VERSION = "human-validation-workflow-v1"

REFERENCE_STATES: tuple[str, ...] = (
    "IDENTIFIED",
    "IN_REVIEW",
    "VALIDATED",
    "REJECTED",
)

DISCLAIMER = (
    "Workflow técnico de validação humana vazio. Estados de referência são "
    "documentais. Sem crédito público, sem comando jurídico e sem homologação "
    "institucional de Gold. Distinto da validação de crédito tributário."
)


def build_human_validation_snapshot() -> dict:
    return {
        "version": HUMAN_VALIDATION_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "publishesPublicCredit": False,
        "legalCommandsEnabled": False,
        "g4Status": "BLOCKED",
        "g5Status": "BLOCKED",
        "referenceStates": list(REFERENCE_STATES),
        "activeItems": [],
        "queue": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }
