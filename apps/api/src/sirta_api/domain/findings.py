"""Technical audit findings shell. Never creates tax credits or legal effects."""

FINDINGS_VERSION = "findings-technical-v1"

DISCLAIMER = (
    "Achados técnicos vazios. Nenhuma ocorrência constitui crédito tributário, "
    "cobrança, notificação ou publicação. Comandos jurídicos desativados até G4/G5."
)


def build_findings_page(*, page: int = 1, size: int = 20) -> dict:
    return {
        "catalogVersion": FINDINGS_VERSION,
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
