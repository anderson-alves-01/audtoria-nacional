"""Controlled municipal restricted upload shell. No real files or samples."""

from sirta_api.domain.errors import ConflictError

MUNICIPAL_UPLOADS_VERSION = "municipal-uploads-technical-v1"

UPLOAD_SLOTS: tuple[dict, ...] = (
    {
        "sourceId": "MUNICIPAL-ISS-RESTRICTED",
        "layoutVersion": "municipal-iss-v1",
        "role": "PRIMARY_FISCAL",
        "accessClassification": "RESTRICTED",
        "quarantineRequired": True,
        "tenantScoped": True,
        "uploadEnabled": False,
        "samplePresent": False,
        "status": "CREDENTIAL_REQUIRED",
    },
    {
        "sourceId": "MUNICIPAL-IPTU-RESTRICTED",
        "layoutVersion": "municipal-iptu-v1",
        "role": "PRIMARY_FISCAL",
        "accessClassification": "RESTRICTED",
        "quarantineRequired": True,
        "tenantScoped": True,
        "uploadEnabled": False,
        "samplePresent": False,
        "status": "CREDENTIAL_REQUIRED",
    },
    {
        "sourceId": "MUNICIPAL-ITBI-RESTRICTED",
        "layoutVersion": "municipal-itbi-v1",
        "role": "PRIMARY_FISCAL",
        "accessClassification": "RESTRICTED",
        "quarantineRequired": True,
        "tenantScoped": True,
        "uploadEnabled": False,
        "samplePresent": False,
        "status": "CREDENTIAL_REQUIRED",
    },
    {
        "sourceId": "MUNICIPAL-DIVIDA-ATIVA",
        "layoutVersion": "municipal-da-v1",
        "role": "PRIMARY_FISCAL",
        "accessClassification": "RESTRICTED",
        "quarantineRequired": True,
        "tenantScoped": True,
        "uploadEnabled": False,
        "samplePresent": False,
        "status": "CREDENTIAL_REQUIRED",
    },
    {
        "sourceId": "MUNICIPAL-PAGAMENTOS",
        "layoutVersion": "municipal-payments-v1",
        "role": "PRIMARY_FISCAL",
        "accessClassification": "RESTRICTED",
        "quarantineRequired": True,
        "tenantScoped": True,
        "uploadEnabled": False,
        "samplePresent": False,
        "status": "CREDENTIAL_REQUIRED",
    },
    {
        "sourceId": "MUNICIPAL-PROCESSOS",
        "layoutVersion": "municipal-cases-v1",
        "role": "PRIMARY_FISCAL",
        "accessClassification": "RESTRICTED",
        "quarantineRequired": True,
        "tenantScoped": True,
        "uploadEnabled": False,
        "samplePresent": False,
        "status": "CREDENTIAL_REQUIRED",
    },
)

DISCLAIMER = (
    "Upload municipal controlado vazio. Schemas e quarentena documentados; "
    "uploadEnabled=false até DPA e G0. Sem amostra real, sem crédito e sem "
    "arquivo municipal nesta fatia."
)


def build_municipal_uploads_panel(*, page: int = 1, size: int = 20) -> dict:
    slots = [dict(row) for row in UPLOAD_SLOTS]
    return {
        "version": MUNICIPAL_UPLOADS_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "uploadEnabled": False,
        "quarantineRequired": True,
        "tenantScoped": True,
        "createsTaxCredit": False,
        "samplePresent": False,
        "g0Status": "BLOCKED",
        "institutionalStatus": "CREDENTIAL_REQUIRED",
        "slots": slots,
        "items": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_municipal_upload_command() -> None:
    raise ConflictError(
        "Upload municipal desativado até DPA e autorização G0. "
        "Shell técnico vazio; sem amostra e sem constituição de crédito."
    )
