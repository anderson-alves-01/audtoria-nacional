"""Official empty payments and installments panel. No invented recovery values."""

from sirta_api.domain.errors import ConflictError

PAYMENTS_PANEL_VERSION = "payments-panel-technical-v1"

DISCLAIMER = (
    "Painel técnico de pagamentos e parcelamentos vazio. Sem recuperação inventada. "
    "Comandos desativados até credencial municipal, DPA e gates G0/G5/G6. "
    "Fonte pública nunca constitui crédito, cobrança ou baixa."
)


def build_payments_panel(*, page: int = 1, size: int = 20) -> dict:
    return {
        "version": PAYMENTS_PANEL_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "recoveryInvented": False,
        "createsTaxCredit": False,
        "legalCommandsEnabled": False,
        "g0Status": "BLOCKED",
        "g5Status": "BLOCKED",
        "g6Status": "LOCAL_GO_OFFICIAL_BLOCKED",
        "credentialStatus": "CREDENTIAL_REQUIRED",
        "items": [],
        "installments": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_payment_command() -> None:
    raise ConflictError(
        "Comando de pagamento/parcelamento desativado até credencial municipal e G0/G5/G6. "
        "Shell técnico vazio; nenhuma baixa, adesão ou recuperação inventada."
    )
