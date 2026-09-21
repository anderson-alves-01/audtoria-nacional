"""Sectoral REFERENCE_ENRICHMENT shell. ANP+ANEEL+BCB+EPE+Anatel+CNES activated; no tax credit."""

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
        "sourceId": "BCB-OLINDA-EXPECTATIVAS",
        "maintainer": "Banco Central",
        "connector": "bcb_olinda_expectativas",
        "structuredOfficialSource": "olinda_odata_expectativas_anuais",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "none",
        "activationGate": "INDICATOR_ALLOWLIST",
        "indicatorAllowlist": [
            "IPCA",
            "IPCA Livres",
            "IPCA Serviços",
            "IPCA Administrados",
            "IPCA Alimentação no domicílio",
            "IPCA Bens industrializados",
            "Selic",
            "Câmbio",
            "PIB Total",
            "PIB Serviços",
            "PIB Agropecuária",
            "PIB Indústria",
            "PIB Formação Bruta de Capital Fixo",
            "PIB Despesa de consumo das famílias",
            "PIB Despesa de consumo da administração pública",
            "PIB Exportação de bens e serviços",
            "PIB Importação de bens e serviços",
            "Produção industrial",
            "IPCA-15",
            "IPC-Fipe",
            "IPA-M",
            "IPA-DI",
            "IGP-M",
            "IGP-DI",
            "INPC",
            "Dívida líquida do setor público",
            "Dívida bruta do governo geral",
            "Balança comercial",
            "Resultado primário",
            "Conta corrente",
            "Resultado nominal",
            "Taxa de desocupação",
            "Investimento direto no país",
        ],
    },
    {
        "sourceId": "BCB-OLINDA-EXPECTATIVAS-MENSAIS",
        "maintainer": "Banco Central",
        "connector": "bcb_olinda_expectativas",
        "structuredOfficialSource": "olinda_odata_expectativas_mensais",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "none",
        "activationGate": "INDICATOR_ALLOWLIST",
        "indicatorAllowlist": [
            "IPCA",
            "IPCA Livres",
            "IPCA Serviços",
            "IPCA Administrados",
            "IPCA Alimentação no domicílio",
            "IPCA Bens industrializados",
            "IGP-M",
            "Câmbio",
            "IPA-M",
            "IPA-DI",
            "IGP-DI",
            "INPC",
        ],
    },
    {
        "sourceId": "CNES-DATASUS",
        "maintainer": "Ministério da Saúde / DATASUS",
        "connector": "cnes_datasus_open",
        "structuredOfficialSource": "demas_api_codigo_uf",
        "status": "TECHNICALLY_APPROVED",
        "ingestAllowed": True,
        "personalDataRisk": "possible_professional_contact_minimized",
        "activationGate": "UF_SCOPED_FIXTURE",
        "territorialScope": "MS",
    },
)

DISCLAIMER = (
    "Fontes setoriais oficiais catalogadas (ANP, ANEEL, EPE, Anatel, BCB, CNES). "
    "ANP, ANEEL, EPE, Anatel e CNES ativadas com escopo UF; BCB com allowlist SGS "
    "432/433 e OLINDA Expectativas Focus anuais (IPCA/Selic/Câmbio/PIB Total/PIB Serviços/"
    "IGP-M/IGP-DI/INPC) e mensais (IPCA/componentes/IGP-M/Câmbio/IPA-M/IPA-DI/"
    "IGP-DI/INPC). "
    "REFERENCE_ENRICHMENT apenas. Não constitui crédito tributário."
)

BLOCKED_SECTORAL_CONNECTORS = frozenset()


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
