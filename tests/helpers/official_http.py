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
}


def snapshot_http_client() -> SnapshotHttpClient:
    payloads = {}
    for url, filename in SNAPSHOT_URLS.items():
        path = SNAPSHOT_DIR / filename
        body = path.read_bytes()
        content_type = "text/html" if filename.endswith(".html") else "application/json"
        payloads[url] = OfficialHttpResponse(
            url=url,
            status_code=200,
            body=body,
            etag=None,
            last_modified=None,
            content_type=content_type,
        )
    return SnapshotHttpClient(payloads)
