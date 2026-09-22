from pathlib import Path

from sirta_api.adapters.ingest.http_client import OfficialHttpResponse, SnapshotHttpClient

SNAPSHOT_DIR = Path("tests/fixtures/official-snapshots")

SNAPSHOT_URLS = {
    (
        "https://servicodados.ibge.gov.br/api/v3/agregados/6579/"
        "periodos/2026/variaveis/9324?localidades=N6[all]"
    ): "ibge-6579.json",
    (
        "https://servicodados.ibge.gov.br/api/v3/agregados/5938/"
        "periodos/2023/variaveis/37|6575?localidades=N6[all]"
    ): "ibge-5938.json",
    (
        "https://servicodados.ibge.gov.br/api/v3/agregados/9509/"
        "periodos/2024/variaveis/707|662|367?localidades=N6[all]"
    ): "ibge-9509.json",
    "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes": "siconfi-entes.json",
    (
        "https://apiapex.tesouro.gov.br/aria/v1/"
        "transferencias_constitucionais/custom/transferencias"
    ): "tesouro-transferencias.json",
    (
        "https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc132.htm"
    ): "planalto-ec132.html",
    "https://legis.senado.leg.br/norma/36873557": "planalto-ec132.html",
    "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm": "planalto-lc214.html",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "af4e7c47-2132-4d9a-bd7c-34e28a210b03/resource/"
        "17336152-2728-4368-9ba2-c3f7821e4acf/download/"
        "transferenciamensalmunicipios202609.csv"
    ): "tesouro-fpm-202608.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "18d5b0ae-8037-461e-8685-3f0d7752a287/download/fundeb-por-municipio.csv"
    ): "tesouro-fundeb-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "18820d64-95fd-4475-b391-e07d62a376ae/download/cide-por-municipio.csv"
    ): "tesouro-cide-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "4ca6aad2-fa9d-48e1-a608-5614578d7df2/download/fex-por-municipio.csv"
    ): "tesouro-fex-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "06aed495-8f46-4852-97f1-ae49822aa179/download/lc-8796-por-municipio.csv"
    ): "tesouro-lc8796-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "d69ff32a-6681-4114-81f0-233bb6b17f58/download/fpm-por-municipio.csv"
    ): "tesouro-fpm-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "f6ad4e51-fc7e-40bb-b35a-3686da7fde2d/download/itr-por-municipio.csv"
    ): "tesouro-itr-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "4248cd95-6d79-4520-9e17-48322eab6259/download/iof-por-municipio.csv"
    ): "tesouro-iof-por-municipio.csv",
    (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "3b5a779d-78f5-4602-a6b7-23ece6d60f27/resource/"
        "c833631a-0933-4e43-a0a5-f77c2fa2267d/download/lc-176-por-municipio.csv"
    ): "tesouro-lc176-por-municipio.csv",
    "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo": "siconfi-rreo.json",
    "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca": "siconfi-dca.json",
    "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf": "siconfi-rgf.json",
    (
        "https://dados.pe.gov.br/dataset/d157c770-7680-454e-9b0f-ddb777de4888/"
        "resource/ff98eec8-cce6-43ba-b8a8-bf55493c554f/download/"
        "transferencias_municipais_2024_.csv"
    ): "pe-transferencias-municipais-2024.csv",
    (
        "https://dados.ba.gov.br/dataset/2ac6387d-80ee-4855-aaba-d6820a5f8a71/"
        "resource/76430704-b1a2-484f-87dc-c86248f4f288/download/2024.csv"
    ): "ba-repasses-municipios-2024.csv",
    (
        "https://dados.mg.gov.br/dataset/5a849756-f55b-4399-860f-b9b08eca0f1a/"
        "resource/ebed720b-5c5e-4e38-878b-be800c6e9967/download/ft_repasse_mun.csv.gz"
    ): "mg-ft-repasse-mun.csv",
    (
        "https://dados.mg.gov.br/dataset/5a849756-f55b-4399-860f-b9b08eca0f1a/"
        "resource/bf4671ef-1131-497f-9580-e720bb8ad585/download/dm_municipio.csv.gz"
    ): "mg-dm-municipio.csv",
    (
        "https://dados.mg.gov.br/dataset/5a849756-f55b-4399-860f-b9b08eca0f1a/"
        "resource/a3a38dfc-2724-4276-9e0f-0b98d4138f09/download/dm_tempo_mensal.csv.gz"
    ): "mg-dm-tempo-mensal.csv",
    (
        "https://dados.es.gov.br/dataset/d85497f8-3dc4-4104-8e18-f242ae82b6ee/"
        "resource/f76f120c-ee95-440c-a77a-2fdace48b1bc/download/"
        "transfestadomunicipios-2024.csv"
    ): "es-transf-estado-municipios-2024.csv",
    (
        "https://dadosabertos.go.gov.br/datastore/dump/343d1fb0-a182-4005-9203-dce168d2ad60"
    ): "go-repasses-municipios-202608.csv",
    (
        "https://goias.gov.br/economia/wp-content/uploads/sites/45/2024/12/"
        "transf-municipios_2024_11.xlsx"
    ): "go-economia-repasses-2024-11.xlsx",
    (
        "https://www.dados.ms.gov.br/datastore/dump/repasses-dos-municipios-01_2026"
    ): "ms-repasses-municipios-202601.csv",
    (
        "https://dados.ro.gov.br/dataset/cfff3fa2-6bb2-4519-bfaa-2f60126dd811/"
        "resource/28a6ff6c-59d4-409e-947d-a38b35bae75b/download/___"
    ): "ro-icms-repasses-2022.csv",
    (
        "https://dados.ro.gov.br/dataset/ae2649de-b047-4555-9dfe-501b6d447fb8/"
        "resource/5deb9684-7411-4824-a904-a855ad68ab66/download/"
        "ipva-portal-2019-2022.csv"
    ): "ro-ipva-repasses-2022.csv",
    (
        "https://dados.ac.gov.br/dataset/e9f7ca08-2c55-45d5-a948-ef25a1acb296/"
        "resource/d0deaa76-c075-4b0d-8cf3-468c5fcb1267/download/"
        "repasse-constitucional-de-icms-para-os-municipios.csv"
    ): "ac-icms-repasses-2021.csv",
    (
        "https://transparencia.ac.gov.br/conteudo/repasse-aos-municipios/dados-exportacao"
    ): "ac-transparencia-repasses-2025-01.json",
    (
        "https://www.ce.gov.br/sefaz/wp-content/uploads/sites/46/2020/08/"
        "1.Portaria-jan-25-ANEXO-UNICO.xls"
    ): "ce-repasses-2025-01.xls",
    (
        "https://www.sefaz.rs.gov.br/Site/MontaArquivo.aspx?al=l_icms_rep_202501"
    ): "rs-icms-repasses-2025-01.xls",
    (
        "https://www.sefaz.rs.gov.br/Site/MontaArquivo.aspx?al=l_ipva_rep_202501"
    ): "rs-ipva-repasses-2025-01.xls",
    (
        "https://www.sefaz.rs.gov.br/Site/MontaArquivo.aspx?al=l_compensacao_perdas_icms_2024"
    ): "rs-compensacao-lc194-2024-10.xls",
    (
        "https://dados.al.gov.br/catalogo/dataset/58cf0b6f-4026-449e-8be8-17a9af3670c6/"
        "resource/1de71f0a-e93e-47e0-b053-9d6dd2abae5b/download/repasses_estaduais.xls"
    ): "al-repasses-estaduais-2021.xls",
    (
        "https://webas.sefaz.pi.gov.br/repasseweb/faces/views/repasseMunicipios.xhtml"
    ): "pi-repasseweb-ipva-2025-01.html",
    (
        "https://www.sefaz.rn.gov.br/wp-json/nextcloud/v1/download?filePath="
        "SEFAZ-GOVRN%2FTranspar%C3%AAncia%2FTransfer%C3%AAncias%20para%20os%20Munic%C3%ADpios%20do%20RN"
        "%2F2026%2FRepasses%20Prefeituras%202026%20-%20Valores%20Repassados%20at%C3%A9%20o%20dia%2031-05-2026.xls"
    ): "rn-repasses-prefeituras-2026-05.xls",
    (
        "https://ui-sgc.sefaz.ma.gov.br/sgc/api/portal/arquivos/public/identificador"
        "?identificador=2185e882-6a8a-4b89-bae7-4d687c2e4515"
    ): "ma-repasses-municipais-2026.xls",
    (
        "https://www4.pr.gov.br/Gestao/portaldatransparencia/repasses/relatorio/"
        "rrepassesmun.jsp?Param_Data=01%2F01%2F2025&Param_Tiporelatorio=MENSAL"
    ): "pr-repasses-mensal-2025-01.html",
    (
        "https://icmsverde.semas.pa.gov.br/Valores_de_Repasses/"
        "Valores-de-repasses-ICMS-Verde-2024.xlsx"
    ): "pa-icms-verde-2024-01.xlsx",
    (
        "https://www.sef.sc.gov.br/api/download?id=5728&nomeArquivo=Anual_2017.csv"
        "&mime=application/vnd.ms-excel"
    ): "sc-anual-2017.csv",
    (
        "https://revendedoresapi.anp.gov.br/v1/combustivel?uf=MS&numeropagina=1"
    ): "anp-revendedores-ms-page1.json",
    (
        "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search?"
        "resource_id=3f841488-80a8-42f2-a6ca-e0c593b228de&"
        "filters=%7B%22SigUF%22%3A%22MS%22%7D&limit=8"
    ): "aneel-indqual-municipio-ms-limit8.json",
    (
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/3?formato=json"
    ): "bcb-sgs-432-ultimos3.json",
    (
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/3?formato=json"
    ): "bcb-sgs-433-ultimos3.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IGP-M%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-igp-m-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27C%C3%A2mbio%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-cambio-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Livres%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-livres-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-servicos-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Administrados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-administrados-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Alimenta%C3%A7%C3%A3o%20no%20domic%C3%ADlio%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-alimentacao-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Bens%20industrializados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-bens-industrializados-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPA-M%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipa-m-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPA-DI%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipa-di-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IGP-DI%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-igp-di-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativaMercadoMensais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27INPC%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-inpc-mensais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Livres%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-livres-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-servicos-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Administrados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-administrados-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Alimenta%C3%A7%C3%A3o%20no%20domic%C3%ADlio%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-alimentacao-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Bens%20industrializados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-bens-industrializados-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27C%C3%A2mbio%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-cambio-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Total%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-total-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-servicos-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Agropecu%C3%A1ria%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-agropecuaria-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoTrimestrais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Ind%C3%BAstria%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-industria-trimestrais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Livres%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-livres-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-servicos-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Administrados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-administrados-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Alimenta%C3%A7%C3%A3o%20no%20domic%C3%ADlio%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-alimentacao-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Bens%20industrializados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-bens-industrializados-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Selic%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-selic-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27C%C3%A2mbio%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-cambio-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Forma%C3%A7%C3%A3o%20Bruta%20de%20Capital%20Fixo%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-fbcf-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Despesa%20de%20consumo%20das%20fam%C3%ADlias%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-despesa-familias-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Despesa%20de%20consumo%20da%20administra%C3%A7%C3%A3o%20p%C3%BAblica%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-despesa-adm-publica-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Exporta%C3%A7%C3%A3o%20de%20bens%20e%20servi%C3%A7os%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-exportacao-bens-servicos-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Importa%C3%A7%C3%A3o%20de%20bens%20e%20servi%C3%A7os%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-importacao-bens-servicos-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Produ%C3%A7%C3%A3o%20industrial%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-producao-industrial-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA-15%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-15-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPC-Fipe%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipc-fipe-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPA-M%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipa-m-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPA-DI%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipa-di-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Total%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-total-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-servicos-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Agropecu%C3%A1ria%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-agropecuaria-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27PIB%20Ind%C3%BAstria%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-pib-industria-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IGP-M%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-igp-m-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IGP-DI%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-igp-di-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27INPC%27%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-inpc-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27D%C3%ADvida%20l%C3%ADquida%20do%20setor%20p%C3%BAblico%27"
        "%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-divida-liquida-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27D%C3%ADvida%20bruta%20do%20governo%20geral%27"
        "%20and%20baseCalculo%20eq%200&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-divida-bruta-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Taxa%20de%20desocupa%C3%A7%C3%A3o%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-taxa-desocupacao-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Investimento%20direto%20no%20pa%C3%ADs%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-investimento-direto-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Balan%C3%A7a%20comercial%27%20and%20"
        "IndicadorDetalhe%20eq%20%27Saldo%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-balanca-saldo-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Balan%C3%A7a%20comercial%27%20and%20"
        "IndicadorDetalhe%20eq%20%27Exporta%C3%A7%C3%B5es%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-balanca-exportacoes-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Balan%C3%A7a%20comercial%27%20and%20"
        "IndicadorDetalhe%20eq%20%27Importa%C3%A7%C3%B5es%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-balanca-importacoes-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Resultado%20prim%C3%A1rio%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-resultado-primario-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Conta%20corrente%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-conta-corrente-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Resultado%20nominal%27"
        "%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-resultado-nominal-anuais-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoSelic?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27Selic%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Reuniao%20asc&"
        "$select=Indicador,Data,Reuniao,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-selic-reuniao-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao12Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-inflacao12m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao12Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IGP-M%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-igp-m-inflacao12m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao12Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Livres%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-livres-inflacao12m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao12Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-servicos-inflacao12m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao24Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-inflacao24m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao24Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Livres%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-livres-inflacao24m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao24Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Servi%C3%A7os%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-servicos-inflacao24m-top8.json",
    (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoInflacao24Meses?$top=8&$format=json&"
        "$filter=Indicador%20eq%20%27IPCA%20Bens%20industrializados%27%20and%20baseCalculo%20eq%201&"
        "$orderby=Data%20desc,Suavizada%20asc&"
        "$select=Indicador,Data,Suavizada,Mediana,Media,baseCalculo"
    ): "bcb-olinda-expectativas-ipca-bens-industrializados-inflacao24m-top8.json",
    (
        "https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/dados-abertos/"
        "Documents/Dados%20brutos.xlsx"
    ): "epe-anuario-dados-brutos-ms-2024.csv",
    (
        "https://www.anatel.gov.br/dadosabertos/paineis_de_dados/meu_municipio/meu_municipio.zip"
    ): "anatel-meu-municipio-acessos-ms-2025-11.csv",
    (
        "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos?codigo_uf=50&limit=8"
    ): "cnes-estabelecimentos-ms-limit8.json",
}


def snapshot_http_client() -> SnapshotHttpClient:
    payloads = {}
    for url, filename in SNAPSHOT_URLS.items():
        path = SNAPSHOT_DIR / filename
        body = path.read_bytes()
        if filename.endswith(".html"):
            content_type = "text/html"
        elif filename.endswith(".csv"):
            content_type = "text/csv"
        else:
            content_type = "application/json"
        payloads[url] = OfficialHttpResponse(
            url=url,
            status_code=200,
            body=body,
            etag=None,
            last_modified=None,
            content_type=content_type,
        )
    return SnapshotHttpClient(payloads)
