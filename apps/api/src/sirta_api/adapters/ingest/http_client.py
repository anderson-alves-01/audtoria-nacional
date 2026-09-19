from dataclasses import dataclass
from time import sleep

import httpx

USER_AGENT = "SIRTA-official-ingest/0.3.19"


@dataclass(frozen=True)
class OfficialHttpResponse:
    url: str
    status_code: int
    body: bytes
    etag: str | None
    last_modified: str | None
    content_type: str | None


class OfficialHttpClient:
    def fetch(self, url: str, *, timeout: float = 120.0, retries: int = 3) -> OfficialHttpResponse:
        headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                with httpx.Client(
                    timeout=timeout, follow_redirects=True, headers=headers
                ) as client:
                    response = client.get(url)
                    if response.status_code >= 500 and attempt < retries - 1:
                        sleep(0.4 * (2**attempt))
                        continue
                    return OfficialHttpResponse(
                        url=str(response.url),
                        status_code=response.status_code,
                        body=response.content,
                        etag=response.headers.get("ETag"),
                        last_modified=response.headers.get("Last-Modified"),
                        content_type=response.headers.get("Content-Type"),
                    )
            except httpx.HTTPError as exc:
                last_error = exc
                sleep(0.4 * (2**attempt))
        if last_error is not None:
            raise last_error
        raise RuntimeError("official HTTP fetch exhausted retries")


class SnapshotHttpClient:
    def __init__(self, payloads: dict[str, OfficialHttpResponse]) -> None:
        self._payloads = payloads

    def fetch(self, url: str, *, timeout: float = 120.0, retries: int = 3) -> OfficialHttpResponse:
        if url in self._payloads:
            return self._payloads[url]
        for prefix, payload in self._payloads.items():
            if url.startswith(prefix):
                return payload
        raise LookupError(f"no official snapshot registered for {url}")
