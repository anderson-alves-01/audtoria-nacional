"""Technical audit cases shell (D5). Distinct from administrative collection cases."""

from sirta_api.domain.errors import ConflictError

AUDIT_CASES_VERSION = "audit-cases-technical-v1"

DISCLAIMER = (
    "Casos de auditoria técnicos vazios. Criação e comandos jurídicos desativados. "
    "Não confundir com cobrança administrativa. Sem crédito público."
)


def build_audit_cases_page(*, page: int = 1, size: int = 20) -> dict:
    return {
        "catalogVersion": AUDIT_CASES_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "legalCommandsEnabled": False,
        "g5Status": "BLOCKED",
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
        "items": [],
        "page": page,
        "size": size,
        "total": 0,
    }


def reject_audit_case_create() -> None:
    raise ConflictError(
        "Criação de caso de auditoria desativada até homologação G4/G5. "
        "Shell técnico vazio; nenhum registro persistido."
    )
