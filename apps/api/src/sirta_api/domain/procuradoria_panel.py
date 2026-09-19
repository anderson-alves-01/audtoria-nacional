"""Official empty Procuradoria workflow. No automatic legal status change."""

from sirta_api.domain.errors import ConflictError

PROCURADORIA_PANEL_VERSION = "procuradoria-panel-technical-v1"

DISCLAIMER = (
    "Workflow técnico da Procuradoria vazio. Sem alteração jurídica automática. "
    "Comandos desativados até autorização municipal e gates G0/G5/G6."
)


def build_procuradoria_panel() -> dict:
    return {
        "version": PROCURADORIA_PANEL_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "legalCommandsEnabled": False,
        "altersLegalStatus": False,
        "createsTaxCredit": False,
        "g0Status": "BLOCKED",
        "g5Status": "BLOCKED",
        "g6Status": "LOCAL_GO_OFFICIAL_BLOCKED",
        "credentialStatus": "CREDENTIAL_REQUIRED",
        "items": [],
        "queue": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_legal_command() -> None:
    raise ConflictError(
        "Comando jurídico da Procuradoria desativado até autorização municipal e G0/G5/G6. "
        "Shell técnico vazio; nenhum encaminhamento ou alteração de status jurídico."
    )
