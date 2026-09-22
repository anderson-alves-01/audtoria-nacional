"""Administrative notifications shell. Real send remains disabled until human approval."""

from sirta_api.domain.errors import ConflictError

NOTIFICATIONS_VERSION = "notifications-technical-v1"

DISCLAIMER = (
    "Notificações administrativas técnicas vazias. Envio real desativado até "
    "aprovação humana (G4/G5). Sem crédito tributário e sem comunicação ao contribuinte."
)


def build_notifications_page(*, page: int = 1, size: int = 20) -> dict:
    return {
        "catalogVersion": NOTIFICATIONS_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "sendEnabled": False,
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


def reject_notification_send() -> None:
    raise ConflictError(
        "Envio de notificação desativado até aprovação humana G4/G5. "
        "Shell técnico vazio; nenhuma mensagem enviada ou persistida."
    )
