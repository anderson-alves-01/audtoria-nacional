from sirta_api.domain.catalog import HOMOLOGATION_PENDING

VALUE_KINDS = frozenset(
    {
        "REFERENCE_QUANTITY",
        "CATALOG_METADATA",
        "COVERAGE_REGISTRY",
        "TRANSFER_AMOUNT_AS_PUBLISHED",
        "FISCAL_STATEMENT_LINE",
        "REGULATORY_DOCUMENT",
    }
)

PRESENTATION = {
    "IBGE-SIDRA": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "População estimada publicada pelo IBGE. Não é crédito tributário nem transferência."
        ),
    },
    "IBGE-SIDRA-PIB": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "PIB municipal publicado pelo IBGE. Não é crédito tributário nem potencial de ISS."
        ),
    },
    "IBGE-SIDRA-CEMP": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Cadastro Central de Empresas (SIDRA 9509): ocupação, massa salarial e "
            "empresas atuantes. Não é base de ISS nem crédito tributário."
        ),
    },
    "SICONFI-ENTES": {
        "valueKind": "COVERAGE_REGISTRY",
        "label": "Cadastro de entes do SICONFI. Não é demonstrativo fiscal (RREO/DCA).",
    },
    "TESOURO-TRANSPARENTE": {
        "valueKind": "CATALOG_METADATA",
        "label": "Dicionário de tipos de transferência. FPM código 3 não é valor transferido.",
    },
    "TESOURO-FPM-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores de FPM publicados pelo Tesouro. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-ITR-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores de ITR publicados pelo Tesouro no CSV mensal. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-IPI-EXP-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores de IPI-Exportação publicados pelo Tesouro no CSV mensal "
            "(frequentemente retenção FUNDEB). Ocorrência para análise, "
            "não crédito nem cobrança."
        ),
    },
    "TESOURO-ROYALTIES-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Royalties publicados pelo Tesouro (FEP/CFEM/ANP/CFH/PEA/ITA). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-LC176-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores LC 176/2020 (ADO25) publicados pelo Tesouro no CSV mensal. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-IOF-OURO-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores IOF-Ouro publicados pelo Tesouro no CSV mensal. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-FUNDEB-COMPLEMENT-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Complementação da União ao FUNDEB (COUN VAAT/VAAR/VAAF) e "
            "AJUSTE FUNDEB publicados pelo Tesouro. Ocorrência para análise, "
            "não crédito nem cobrança."
        ),
    },
    "TESOURO-FUNDEB-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores FUNDEB distribuídos aos municípios publicados pelo Tesouro "
            "(COINT). Distinto de complementação COUN/AJUSTE e de retenções. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-CIDE-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores CIDE-Combustíveis publicados pelo Tesouro (COINT). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-FEX-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores FEX publicados pelo Tesouro (COINT). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-LC87-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores LC 87/96 (Lei Kandir) publicados pelo Tesouro (COINT). "
            "Série histórica oficial com valores não nulos até 2018; "
            "colunas 2019–2020 publicadas vazias. Ocorrência para análise, "
            "não crédito nem cobrança."
        ),
    },
    "TESOURO-FPM-COINT-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores FPM distribuídos aos municípios publicados pelo Tesouro "
            "(COINT). Distinto do CSV mensal TESOURO-FPM-VALORES. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-ITR-COINT-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores ITR distribuídos aos municípios publicados pelo Tesouro "
            "(COINT). Distinto do CSV mensal TESOURO-ITR-VALORES. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "TESOURO-IOF-OURO-COINT-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores IOF-Ouro distribuídos aos municípios publicados pelo Tesouro "
            "(COINT). Distinto do CSV mensal TESOURO-IOF-OURO-VALORES. Série "
            "esparsa por município. Ocorrência para análise, não crédito."
        ),
    },
    "TESOURO-LC176-COINT-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores LC 176/2020 (ADO25) distribuídos aos municípios publicados "
            "pelo Tesouro (COINT). Distinto do CSV mensal TESOURO-LC176-VALORES. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (PE ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (PE ativado; zero é valor oficial). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PE-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (PE ativado via CSV dados.pe.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-BA-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (BA ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-BA-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (BA ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-BA-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (BA ativado via CSV dados.ba.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MG-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (MG ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MG-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (MG ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MG-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (MG ativado via ft_repasse_mun). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ES-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (ES ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ES-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (ES ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ES-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (ES ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ES-CIDE-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Cota-parte CIDE publicada (ES ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ES-FRD-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Fundo de Redução das Desigualdades publicado (ES ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ES-COMPENSACAO-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Compensação Financeira publicada (ES ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-GO-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (GO ativado via DataStore). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-GO-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada "
            "(GO ativado via XLSX Secretaria da Economia). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-GO-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI-Exportação estadual publicada "
            "(GO ativado via XLSX Secretaria da Economia). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MS-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (MS ativado via DataStore). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MS-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (MS ativado via DataStore). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MS-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI-Exportação estadual publicada "
            "(MS ativado via DataStore, Tipo_Repasse REPASSE DE IPI EXPORTAÇÃO). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MS-CIDE-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Cota-parte CIDE publicada "
            "(MS ativado via DataStore, Tipo_Repasse REPASSE DA CIDE). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RO-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (RO ativado via dados.ro.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RO-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (RO ativado via dados.ro.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AC-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (AC ativado via dados.ac.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AC-ICMS-TRANSPARENCIA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual mensal publicada "
            "(AC ativado via Transparência POST+CSRF JSON, valor_icms). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AC-FUNDEB-TRANSPARENCIA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valor FUNDEB publicado no export Transparência AC "
            "(valor_fundeb; série mensal POST+CSRF JSON). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AC-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada "
            "(AC ativado via Transparência POST+CSRF JSON). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-CE-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (CE ativado via SEFAZ XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-CE-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (CE ativado via SEFAZ XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-CE-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (CE ativado via SEFAZ XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RS-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (RS ativado via SEFAZ MontaArquivo). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RS-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (RS ativado via SEFAZ MontaArquivo). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RS-COMPENSACAO-LC194-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Compensação de perdas de ICMS LC 194/22 publicada "
            "(RS ativado via SEFAZ MontaArquivo). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AL-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (AL ativado via dados.al.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AL-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (AL ativado via dados.al.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AL-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (AL ativado via dados.al.gov.br). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-AL-ROYALTY-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Royalties estaduais publicados (AL ativado via coluna Royalties Total "
            "no XLS dados.al.gov.br). Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PI-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada "
            "(PI ativado via SEFAZ Repasse WEB HTML). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RN-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (RN ativado via SEFAZ Nextcloud XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RN-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (RN ativado via SEFAZ Nextcloud XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-RN-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI estadual publicada (RN ativado via SEFAZ Nextcloud XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MA-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (MA ativado via SEFAZ SGC XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MA-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (MA ativado via SEFAZ SGC XLS). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-MA-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI-Exportação/FPEX estadual publicada "
            "(MA ativado via SEFAZ SGC XLS, aba FPEX). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PR-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada "
            "(PR ativado via relatório HTML SEFA/Transparência). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PR-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada "
            "(PR ativado via relatório HTML SEFA/Transparência). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PR-IPI-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPI-Exportação/FPEX estadual publicada "
            "(PR ativado via coluna Fundo de Exportação no HTML SEFA). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PR-ROYALTY-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Royalties de petróleo estaduais publicados "
            "(PR ativado via coluna Royalties no HTML SEFA). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-PA-ICMS-VERDE-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Componente ecológico (ICMS Verde, até 8%) da cota-parte de ICMS do Pará "
            "(SEMAS XLSX mensal). Não é a cota-parte total de ICMS nem IPVA. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ANP-REVENDEDORES": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Contagem de postos revendedores ANP por município (escopo UF). "
            "Referência setorial; não constitui crédito tributário."
        ),
    },
    "ANEEL-DADOS-ABERTOS": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Contagem IndQual de conjuntos de unidades consumidoras por município "
            "(escopo UF). Referência setorial; não constitui crédito tributário."
        ),
    },
    "BCB-SGS-OLINDA": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Séries macroeconômicas SGS do Banco Central (allowlist). "
            "Contexto setorial; não constitui crédito tributário."
        ),
    },
    "BCB-OLINDA-EXPECTATIVAS": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Expectativas Focus anuais OLINDA do Banco Central "
            "(allowlist IPCA/Selic/Câmbio/PIB Total/PIB Serviços/"
            "PIB Agropecuária/PIB Indústria/IGP-M/IGP-DI/INPC). "
            "Contexto setorial; não constitui crédito tributário."
        ),
    },
    "BCB-OLINDA-EXPECTATIVAS-MENSAIS": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Expectativas Focus mensais OLINDA do Banco Central "
            "(allowlist IPCA/IPCA Livres/IPCA Serviços/IPCA Administrados/"
            "IPCA Alimentação/IPCA Bens industrializados/IGP-M/Câmbio). "
            "Contexto setorial; não constitui crédito tributário."
        ),
    },
    "EPE-DADOS-ABERTOS": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Contagem de consumidores do Anuário EPE (Dados brutos) por UF/competência. "
            "Referência setorial; não constitui crédito tributário."
        ),
    },
    "ANATEL-DADOS-ABERTOS": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Acessos de banda larga fixa Anatel Meu Município por IBGE7 (escopo UF). "
            "Referência setorial; não constitui crédito tributário."
        ),
    },
    "CNES-DATASUS": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "Contagem de estabelecimentos CNES/DATASUS por município (escopo UF). "
            "Referência setorial; não constitui crédito tributário."
        ),
    },
    "SICONFI-RREO": {
        "valueKind": "FISCAL_STATEMENT_LINE",
        "label": "Linhas do RREO municipal. Não constituem crédito tributário.",
    },
    "SICONFI-DCA": {
        "valueKind": "FISCAL_STATEMENT_LINE",
        "label": "Linhas do DCA/FINBRA. Não constituem crédito tributário.",
    },
    "SICONFI-RGF": {
        "valueKind": "FISCAL_STATEMENT_LINE",
        "label": "Linhas do RGF municipal. Não constituem crédito tributário.",
    },
    "PLANALTO-LEGISLACAO": {
        "valueKind": "REGULATORY_DOCUMENT",
        "label": "Documento regulatório. binding=false, operational=false, homologated=false.",
    },
    "PLANALTO-LC-214": {
        "valueKind": "REGULATORY_DOCUMENT",
        "label": (
            "Lei Complementar 214/2025 preservada. "
            "binding=false, operational=false, homologated=false."
        ),
    },
}


def presentation_for(source_id: str) -> dict:
    base = PRESENTATION.get(
        source_id,
        {
            "valueKind": "REFERENCE_QUANTITY",
            "label": "Dado oficial de referência. Não é crédito tributário.",
        },
    )
    financial = base["valueKind"] in {"TRANSFER_AMOUNT_AS_PUBLISHED", "FISCAL_STATEMENT_LINE"}
    return {
        **base,
        "createsTaxCredit": False,
        "createsCollection": False,
        "financial": financial,
        "homologationStatus": HOMOLOGATION_PENDING,
        "isFinancialTransferValue": base["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED",
        "isFiscalStatement": base["valueKind"] == "FISCAL_STATEMENT_LINE",
        "isCatalogMetadata": base["valueKind"] == "CATALOG_METADATA",
        "isCoverageRegistry": base["valueKind"] == "COVERAGE_REGISTRY",
    }


def assert_gold_lineage_complete(line: dict) -> None:
    required = (
        "silverRowId",
        "bronzeSha256",
        "landingManifestPath",
        "officialUrl",
        "checksumSha256",
    )
    missing = [key for key in required if not line.get(key)]
    if missing:
        raise ValueError(f"Gold line is missing lineage fields: {missing}")
    if line.get("layer") == "quarantine":
        raise ValueError("Quarantined records cannot be published as Gold")


def coverage_divergence(items: list[dict]) -> dict | None:
    by_source = {item.get("sourceId"): item.get("coverageCount") for item in items}
    ibge = by_source.get("IBGE-SIDRA")
    siconfi = by_source.get("SICONFI-ENTES")
    pib = by_source.get("IBGE-SIDRA-PIB")
    if ibge is None or siconfi is None:
        return None
    if ibge == siconfi and (pib is None or pib == ibge):
        return None
    explanation = (
        "A cobertura municipal difere entre IBGE 6579, SICONFI/entes e IBGE 5938. "
        "A diferença 5.571 versus 5.570 é cobertura pendente de homologação, "
        "não ocorrência administrativa nem crédito tributário."
    )
    return {
        "sourceId": "COVERAGE-DIVERGENCE",
        "indicator": "municipal_coverage_divergence",
        "maintainer": "SIRTA",
        "dataset": "COVERAGE-CHECK",
        "competence": "as_published",
        "lastExtractedAt": "",
        "formula": (
            "Contagem de municípios na série IBGE 6579 versus entes municipais SICONFI "
            "versus municípios da série IBGE 5938."
        ),
        "methodologyVersion": "coverage-divergence-v1",
        "coverageCount": abs(int(ibge or 0) - int(siconfi or 0)),
        "qualityLevel": "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION",
        "homologationStatus": HOMOLOGATION_PENDING,
        "officialUrl": "https://sidra.ibge.gov.br/tabela/6579",
        "lineage": {"status": "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION"},
        "quarantinedCount": 0,
        "numericTotal": None,
        "createsTaxCredit": False,
        "valueKind": "COVERAGE_REGISTRY",
        "financial": False,
        "presentation": explanation,
        "ibgePopulationMunicipalities": ibge,
        "siconfiMunicipalEntes": siconfi,
        "ibgePibMunicipalities": pib,
        "status": "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION",
        "explanation": explanation,
    }
