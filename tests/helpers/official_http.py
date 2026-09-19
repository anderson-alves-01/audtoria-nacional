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
        "https://www.dados.ms.gov.br/datastore/dump/repasses-dos-municipios-01_2026"
    ): "ms-repasses-municipios-202601.csv",
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
