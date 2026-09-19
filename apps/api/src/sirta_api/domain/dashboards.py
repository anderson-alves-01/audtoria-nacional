DASHBOARDS = (
    {
        "id": "executivo",
        "path": "/executivo",
        "title": "Painel executivo",
        "goldSourceIds": ("IBGE-SIDRA", "IBGE-SIDRA-PIB", "SICONFI-ENTES", "COVERAGE-DIVERGENCE"),
        "emptyReason": "Sem Gold oficial publicado para o recorte executivo.",
        "commandsDisabled": True,
    },
    {
        "id": "financeiro",
        "path": "/financeiro",
        "title": "Financeiro e ROI",
        "goldSourceIds": ("TESOURO-FPM-VALORES", "SICONFI-RREO", "SICONFI-DCA", "SICONFI-RGF"),
        "emptyReason": "ROI e recuperação exigem valores elegíveis e recebidos reais homologados.",
        "commandsDisabled": True,
    },
    {
        "id": "economia",
        "path": "/economia",
        "title": "Contexto econômico e potencial ISS",
        "goldSourceIds": ("IBGE-SIDRA-PIB", "IBGE-SIDRA", "ANP-REVENDEDORES", "ANEEL-DADOS-ABERTOS"),
        "emptyReason": "PIB e população não são potencial de ISS nem crédito constituído.",
        "commandsDisabled": True,
    },
    {
        "id": "operacao",
        "path": "/operacao",
        "title": "Operacional e SLA",
        "goldSourceIds": (),
        "emptyReason": "Sem carga municipal autorizada. SLA permanece vazio.",
        "commandsDisabled": True,
    },
    {
        "id": "achados",
        "path": "/achados",
        "title": "Achados e casos",
        "goldSourceIds": (),
        "emptyReason": "Sem achados oficiais. Módulo vazio até evidência municipal autorizada.",
        "commandsDisabled": True,
    },
    {
        "id": "cobranca",
        "path": "/cobranca",
        "title": "Cobrança administrativa",
        "goldSourceIds": (),
        "emptyReason": "Comando de cobrança desativado até G0/G4 e homologação humana.",
        "commandsDisabled": True,
    },
    {
        "id": "pagamentos",
        "path": "/pagamentos",
        "title": "Pagamentos e parcelamentos",
        "goldSourceIds": (),
        "emptyReason": (
            "CREDENTIAL_REQUIRED — painel oficial /v1/payments vazio; sem recuperação inventada."
        ),
        "commandsDisabled": True,
    },
    {
        "id": "divida-ativa",
        "path": "/divida-ativa",
        "title": "Dívida ativa",
        "goldSourceIds": (),
        "emptyReason": (
            "CREDENTIAL_REQUIRED — painel oficial /v1/active-debt vazio; inscrição desativada."
        ),
        "commandsDisabled": True,
    },
    {
        "id": "transferencias",
        "path": "/transferencias",
        "title": "Transferências",
        "goldSourceIds": (
            "TESOURO-FPM-VALORES",
            "TESOURO-TRANSPARENTE",
            "ESTADO-ICMS-QUOTA",
            "ESTADO-IPVA-QUOTA",
            "ESTADO-BA-ICMS-QUOTA",
            "ESTADO-BA-IPVA-QUOTA",
            "ESTADO-MG-ICMS-QUOTA",
            "ESTADO-MG-IPVA-QUOTA",
            "ESTADO-ES-ICMS-QUOTA",
            "ESTADO-ES-IPVA-QUOTA",
            "ESTADO-GO-IPVA-QUOTA",
            "ESTADO-MS-ICMS-QUOTA",
            "ESTADO-MS-IPVA-QUOTA",
        ),
        "emptyReason": (
            "Somente valores oficiais publicados. Dicionário FPM não é valor transferido. "
            "Conciliação previsto/realizado em /v1/transfer-reconciliation "
            "(ocorrência, não crédito)."
        ),
        "commandsDisabled": True,
    },
    {
        "id": "ibs-cbs",
        "path": "/ibs-cbs",
        "title": "IBS/CBS",
        "goldSourceIds": ("PLANALTO-LEGISLACAO", "PLANALTO-LC-214"),
        "emptyReason": "Documento regulatório não vinculante. binding=false, operational=false.",
        "commandsDisabled": True,
    },
    {
        "id": "qualidade",
        "path": "/qualidade",
        "title": "Qualidade, quarentena e lineage",
        "goldSourceIds": (),
        "emptyReason": "Exibe Gold oficial publicado e linhas em quarentena, sem interpolação.",
        "commandsDisabled": True,
        "includeAllGold": True,
    },
    {
        "id": "auditoria",
        "path": "/auditoria",
        "title": "Segurança e auditoria",
        "goldSourceIds": (),
        "emptyReason": "Trilha de auditoria vazia até operação autorizada.",
        "commandsDisabled": True,
    },
    {
        "id": "gates",
        "path": "/gates",
        "title": "Governança e gates",
        "goldSourceIds": (),
        "emptyReason": "Gates humanos permanecem BLOCKED. Esta tela não aprova G0/G1/G4/G9/G10.",
        "commandsDisabled": True,
    },
    {
        "id": "publico",
        "path": "/publico",
        "title": "Público agregado",
        "goldSourceIds": (),
        "emptyReason": "Agregados somente de Gold oficial. Sem dado sintético.",
        "commandsDisabled": True,
        "includeAllGold": True,
    },
    {
        "id": "prontidao",
        "path": "/prontidao",
        "title": "Prontidão para piloto e produção",
        "goldSourceIds": (),
        "emptyReason": (
            "Checklist técnico em /v1/pilot-readiness. G9/G10 BLOCKED sem município e aceites."
        ),
        "commandsDisabled": True,
    },
)


def dashboard_by_id(dashboard_id: str) -> dict | None:
    for item in DASHBOARDS:
        if item["id"] == dashboard_id:
            return item
    return None
