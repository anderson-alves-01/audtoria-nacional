from dataclasses import dataclass

from sirta_api.domain.errors import ConflictError

STATUS_NON_BINDING = "NON_BINDING"
CATALOG_VERSION = "catalog-official-docs-v1"
PRESERVED_DOC_SOURCE_IDS = ("PLANALTO-LEGISLACAO", "PLANALTO-LC-214")


@dataclass(frozen=True)
class RegulatoryCatalogItem:
    code: str
    title: str
    source: str
    kind: str
    affected_system: str
    notes: str
    version: str = CATALOG_VERSION


SYNTHETIC_CATALOG: tuple[RegulatoryCatalogItem, ...] = (
    RegulatoryCatalogItem(
        code="EC-132-2023",
        title="EC 132/2023 — marco constitucional (documento oficial preservável)",
        source="https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc132.htm",
        kind="NORM",
        affected_system="iss-cadastro",
        notes=(
            "Aponta para PLANALTO-LEGISLACAO quando Gold preservado existir. "
            "Datas, alíquotas e obrigações oficiais exigem homologação. binding=false."
        ),
    ),
    RegulatoryCatalogItem(
        code="LC-214-2025",
        title="LC 214/2025 — IBS/CBS (documento oficial preservável)",
        source="https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm",
        kind="NORM",
        affected_system="regulatory-monitor",
        notes=(
            "Aponta para PLANALTO-LC-214 quando Gold preservado existir. "
            "Nenhuma regra, alíquota ou prazo é inferido. binding=false."
        ),
    ),
    RegulatoryCatalogItem(
        code="CGIBS-PORTAL",
        title="Comitê Gestor do IBS — portal de acompanhamento",
        source="https://www.cgibs.gov.br/",
        kind="NORM",
        affected_system="regulatory-monitor",
        notes="Fonte aprovada no catálogo. Nenhum leiaute operacional foi homologado aqui.",
    ),
    RegulatoryCatalogItem(
        code="RFB-CBS-PORTAL",
        title="Receita Federal — acompanhamento CBS",
        source="https://www.gov.br/receitafederal/",
        kind="NORM",
        affected_system="regulatory-monitor",
        notes="Fonte aprovada no catálogo. Uso operacional bloqueado até homologação.",
    ),
    RegulatoryCatalogItem(
        code="LAYOUT-IBS-CBS-PLACEHOLDER",
        title="Leiaute IBS/CBS — placeholder não operacional",
        source="synthetic-catalog",
        kind="LAYOUT",
        affected_system="data-platform",
        notes="Catálogo de leiaute sem campos oficiais. Não usar em integração.",
    ),
    RegulatoryCatalogItem(
        code="ISS-IMPACT-MAP-SYNTHETIC",
        title="Mapa de impacto ISS — simulação não vinculante",
        source="synthetic-catalog",
        kind="IMPACT",
        affected_system="iss-cadastro",
        notes="Simulação local. Não infere obrigação legal nem perda de receita.",
    ),
    RegulatoryCatalogItem(
        code="READINESS-CADASTRO-SYNTHETIC",
        title="Prontidão cadastral — checklist sintético",
        source="synthetic-catalog",
        kind="READINESS",
        affected_system="cadastro-360",
        notes="Checklist tecnológico. Não homologa cadastro municipal.",
    ),
    RegulatoryCatalogItem(
        code="SIMULATION-NON-BINDING",
        title="Simulação IBS/CBS — não vinculante",
        source="synthetic-catalog",
        kind="SIMULATION",
        affected_system="indicators",
        notes="Resultados hipotéticos. Proibido publicar como KPI operacional.",
    ),
    RegulatoryCatalogItem(
        code="TRAINING-PLAN-PLACEHOLDER",
        title="Plano de capacitação — rascunho local",
        source="synthetic-catalog",
        kind="TRAINING",
        affected_system="governance",
        notes="Capacitação não iniciada. G0 municipal permanece bloqueado.",
    ),
)


def operational_use_allowed(*, binding: bool, status: str, homologated: bool) -> bool:
    return binding is True and homologated is True and status == "HOMOLOGATED"


def assert_not_operational(*, binding: bool, status: str, homologated: bool = False) -> None:
    if operational_use_allowed(binding=binding, status=status, homologated=homologated):
        return
    raise ConflictError(
        "Regulatory item cannot be used operationally without official homologation"
    )
