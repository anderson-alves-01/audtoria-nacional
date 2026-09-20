from dataclasses import dataclass
from time import sleep
from urllib.parse import unquote

import httpx

USER_AGENT = "SIRTA-official-ingest/0.3.42"


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

    def fetch_post(
        self,
        url: str,
        *,
        data: dict[str, str],
        headers: dict[str, str] | None = None,
        timeout: float = 120.0,
        retries: int = 3,
        cookies: dict[str, str] | None = None,
    ) -> OfficialHttpResponse:
        base_headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json,*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if headers:
            base_headers.update(headers)
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                with httpx.Client(
                    timeout=timeout,
                    follow_redirects=True,
                    headers=base_headers,
                    cookies=cookies or {},
                ) as client:
                    response = client.post(url, data=data)
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
        raise RuntimeError("official HTTP POST exhausted retries")

    def fetch_csrf_form_post(
        self,
        *,
        page_url: str,
        post_url: str,
        form_data: dict[str, str],
        timeout: float = 120.0,
    ) -> OfficialHttpResponse:
        """GET HTML page for CSRF cookie/meta, then POST form to official endpoint."""
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
            page = client.get(page_url)
            if page.status_code >= 400:
                return OfficialHttpResponse(
                    url=str(page.url),
                    status_code=page.status_code,
                    body=page.content,
                    etag=page.headers.get("ETag"),
                    last_modified=page.headers.get("Last-Modified"),
                    content_type=page.headers.get("Content-Type"),
                )
            html = page.text
            csrf = ""
            marker = 'name="csrf-token" content="'
            start = html.find(marker)
            if start >= 0:
                start += len(marker)
                end = html.find('"', start)
                if end > start:
                    csrf = html[start:end]
            xsrf = unquote(page.cookies.get("XSRF-TOKEN") or "")
            payload = dict(form_data)
            if csrf:
                payload.setdefault("_token", csrf)
            post_headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/json,*/*",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": page_url,
            }
            if csrf:
                post_headers["X-CSRF-TOKEN"] = csrf
            if xsrf:
                post_headers["X-XSRF-TOKEN"] = xsrf
            response = client.post(post_url, data=payload, headers=post_headers)
            return OfficialHttpResponse(
                url=str(response.url),
                status_code=response.status_code,
                body=response.content,
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
                content_type=response.headers.get("Content-Type"),
            )


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

    def fetch_post(
        self,
        url: str,
        *,
        data: dict[str, str],
        headers: dict[str, str] | None = None,
        timeout: float = 120.0,
        retries: int = 3,
        cookies: dict[str, str] | None = None,
    ) -> OfficialHttpResponse:
        return self.fetch(url, timeout=timeout, retries=retries)

    def fetch_csrf_form_post(
        self,
        *,
        page_url: str,
        post_url: str,
        form_data: dict[str, str],
        timeout: float = 120.0,
    ) -> OfficialHttpResponse:
        return self.fetch(post_url, timeout=timeout)
