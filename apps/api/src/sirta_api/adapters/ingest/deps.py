from sirta_api.adapters.ingest.http_client import OfficialHttpClient


def get_official_http_client() -> OfficialHttpClient:
    return OfficialHttpClient()
