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
