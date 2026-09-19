"""Official empty active-debt panel. Inscription remains disabled."""

from sirta_api.domain.errors import ConflictError

ACTIVE_DEBT_PANEL_VERSION = "active-debt-panel-technical-v1"

DISCLAIMER = (
    "Painel técnico de dívida ativa vazio. Inscrição desativada até Procuradoria, "
    "DPA e gates G0/G5/G6. Sem crédito tributário e sem alteração jurídica automática."
)


def build_active_debt_panel() -> dict:
    return {
        "version": ACTIVE_DEBT_PANEL_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "inscriptionEnabled": False,
        "createsTaxCredit": False,
        "legalCommandsEnabled": False,
        "g0Status": "BLOCKED",
        "g5Status": "BLOCKED",
        "g6Status": "LOCAL_GO_OFFICIAL_BLOCKED",
        "credentialStatus": "CREDENTIAL_REQUIRED",
        "items": [],
        "queue": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_inscription_command() -> None:
    raise ConflictError(
        "Inscrição em dívida ativa desativada até autorização municipal e G0/G5/G6. "
        "Shell técnico vazio; nenhuma inscrição ou certidão gerada."
    )
