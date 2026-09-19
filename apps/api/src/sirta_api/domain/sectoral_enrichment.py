"""Sectoral REFERENCE_ENRICHMENT shell. ANP+ANEEL+BCB+EPE+Anatel activated; no tax credit."""

from sirta_api.domain.errors import ConflictError

SECTORAL_ENRICHMENT_VERSION = "sectoral-enrichment-technical-v1"

SECTORAL_SOURCES: tuple[dict, ...] = (
    {
        "sourceId": "ANP-REVENDEDORES",
        "maintainer": "ANP",
        "connector": "anp_revendedores_api",
        "structuredOfficialSource": "rest_api_verified",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "possible_establishment_cnpj_minimized",
        "activationGate": "UF_SCOPED_FIXTURE",
        "territorialScope": "MS",
    },
    {
        "sourceId": "ANEEL-DADOS-ABERTOS",
        "maintainer": "ANEEL",
        "connector": "aneel_ckan_open",
        "structuredOfficialSource": "ckan_datastore_indqual_municipio",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "none",
        "activationGate": "UF_SCOPED_FIXTURE",
        "territorialScope": "MS",
    },
    {
        "sourceId": "EPE-DADOS-ABERTOS",
        "maintainer": "EPE",
        "connector": "epe_open_files",
        "structuredOfficialSource": "anuario_dados_brutos_xlsx",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "none",
        "activationGate": "UF_SCOPED_FIXTURE",
        "territorialScope": "MS",
    },
    {
        "sourceId": "ANATEL-DADOS-ABERTOS",
        "maintainer": "Anatel",
        "connector": "anatel_dados_gov",
        "structuredOfficialSource": "meu_municipio_zip_csv_ibge7",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "none",
        "activationGate": "UF_SCOPED_FIXTURE",
        "territorialScope": "MS",
    },
    {
        "sourceId": "BCB-SGS-OLINDA",
        "maintainer": "Banco Central",
        "connector": "bcb_sgs_olinda",
        "structuredOfficialSource": "sgs_json_allowlist",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "none",
        "activationGate": "SERIES_ALLOWLIST",
        "seriesAllowlist": [432, 433],
    },
    {
        "sourceId": "CNES-DATASUS",
        "maintainer": "Ministério da Saúde / DATASUS",
        "connector": "cnes_datasus_open",
        "structuredOfficialSource": "open_data_portal_and_competence_files",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "possible_professional_contact_minimized",
        "activationGate": "TERRITORIAL_SCOPE",
    },
)

DISCLAIMER = (
    "Fontes setoriais oficiais catalogadas (ANP, ANEEL, EPE, Anatel, BCB, CNES). "
    "ANP, ANEEL, EPE e Anatel ativadas com escopo UF; BCB com allowlist SGS 432/433; "
    "CNES ingestAllowed=false. REFERENCE_ENRICHMENT apenas. "
    "Não constitui crédito tributário."
)

BLOCKED_SECTORAL_CONNECTORS = frozenset(
    {
        "cnes_datasus_open",
    }
)


def build_sectoral_enrichment_panel(*, page: int = 1, size: int = 20) -> dict:
    sources = [dict(row) for row in SECTORAL_SOURCES]
    ingest_enabled = any(bool(row.get("ingestAllowed")) for row in sources)
    any_approved = any(row.get("status") == "TECHNICALLY_APPROVED" for row in sources)
    return {
        "version": SECTORAL_ENRICHMENT_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "ingestEnabled": ingest_enabled,
        "sourceRole": "REFERENCE_ENRICHMENT",
        "institutionalStatus": ("PARTIAL_TECHNICAL_ACTIVATION" if any_approved else "DISCOVERED"),
        "sources": sources,
        "items": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_sectoral_enrichment_command() -> None:
    raise ConflictError(
        "Enriquecimento setorial desativado até ativação técnica por fonte. "
        "Shell vazio; sem carga e sem constituição de crédito."
    )
